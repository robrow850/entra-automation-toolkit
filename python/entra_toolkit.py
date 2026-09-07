"""Offline identity reporting exercises; no network calls or tenant mutations."""
import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def timestamp(value):
    """Require an explicit timezone so stale classifications are reproducible."""
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def load_users(path):
    users = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(users, list):
        raise ValueError("Expected a JSON array of normalized users")
    seen = set()
    for user in users:
        if not isinstance(user, dict):
            raise ValueError("Each user must be an object")
        for field in ("id", "displayName", "userPrincipalName"):
            if not isinstance(user.get(field), str) or not user[field].strip():
                raise ValueError("Missing or invalid " + field)
        if user["id"] in seen:
            raise ValueError("Duplicate user id: " + user["id"])
        seen.add(user["id"])
        if type(user.get("accountEnabled")) is not bool:
            raise ValueError("accountEnabled must be a JSON boolean")
        for field in ("createdDateTime", "lastSuccessfulSignInDateTime"):
            value = user.get(field)
            if value is not None:
                if not isinstance(value, str):
                    raise ValueError(field + " must be a timestamp or null")
                timestamp(value)
    return users


def user_report(users):
    return [{key: user.get(key) for key in (
        "id", "displayName", "userPrincipalName", "accountEnabled",
        "createdDateTime", "lastSuccessfulSignInDateTime"
    )} for user in users]


def stale_report(users, days, as_of):
    """Candidates use successful sign-ins only; unknown evidence stays unknown."""
    if days < 1:
        raise ValueError("days must be positive")
    if as_of.tzinfo is None:
        raise ValueError("as_of must include a timezone")
    cutoff = as_of - timedelta(days=days)
    result = []
    for user in users:
        last = user.get("lastSuccessfulSignInDateTime")
        created = user.get("createdDateTime")
        last_date = timestamp(last) if last else None
        created_date = timestamp(created) if created else None
        if ((last_date and last_date > as_of) or
                (created_date and created_date > as_of) or
                (last_date and created_date and last_date < created_date)):
            status = "invalidTimeline"
        elif not user["accountEnabled"]:
            status = "disabled"
        elif last_date is None:
            status = "unknownActivity"
        elif last_date <= cutoff:
            status = "staleCandidate"
        else:
            status = "recentActivity"
        result.append({"id": user["id"], "userPrincipalName": user["userPrincipalName"],
                       "status": status, "lastSuccessfulSignInDateTime": last,
                       "asOf": as_of.isoformat(), "thresholdDays": days})
    return result


def review_packet(users, memberships):
    """Build a human review queue; never approve, revoke, or provision access."""
    by_id = {user["id"]: user for user in users}
    if not isinstance(memberships, list):
        raise ValueError("Expected a JSON array of memberships")
    rows, seen = [], set()
    for membership in memberships:
        if not isinstance(membership, dict):
            raise ValueError("Each membership must be an object")
        for field in ("userId", "resourceId", "resourceName", "reviewer"):
            if not isinstance(membership.get(field), str) or not membership[field].strip():
                raise ValueError("Missing or invalid membership " + field)
        if membership["userId"] not in by_id:
            raise ValueError("Membership references an unknown user")
        pair = (membership["userId"], membership["resourceId"])
        if pair in seen:
            raise ValueError("Duplicate user/resource membership")
        seen.add(pair)
        rows.append({"userId": membership["userId"],
                     "userPrincipalName": by_id[membership["userId"]]["userPrincipalName"],
                     "resourceId": membership["resourceId"],
                     "resourceName": membership["resourceName"],
                     "reviewer": membership["reviewer"], "decision": "Pending",
                     "justification": ""})
    return rows


def csv_cell(value):
    # Escape spreadsheet formula prefixes in imported text, including leading whitespace.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", choices=("users", "stale", "review"))
    parser.add_argument("--users", type=Path, required=True)
    parser.add_argument("--memberships", type=Path)
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--as-of", default=datetime.now(timezone.utc).isoformat())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        users = load_users(args.users)
        if args.workflow == "users":
            rows = user_report(users)
        elif args.workflow == "stale":
            rows = stale_report(users, args.days, timestamp(args.as_of))
        else:
            if args.memberships is None:
                parser.error("review requires --memberships")
            rows = review_packet(users, json.loads(args.memberships.read_text(encoding="utf-8-sig")))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation protects earlier reports and input files from overwrites.
        with args.output.open("x", encoding="utf-8", newline="") as stream:
            if args.workflow == "review":
                writer = csv.DictWriter(stream, fieldnames=("userId", "userPrincipalName",
                    "resourceId", "resourceName", "reviewer", "decision", "justification"))
                writer.writeheader()
                writer.writerows({k: csv_cell(v) for k, v in row.items()} for row in rows)
            else:
                json.dump(rows, stream, indent=2)
                stream.write("\n")
    except (ValueError, OSError) as error:
        parser.exit(2, "Error: " + str(error) + "\n")


if __name__ == "__main__":
    main()
