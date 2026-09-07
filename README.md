# Entra Automation Toolkit

Robert Rowan's identity automation portfolio starter: equivalent PowerShell and
Python workflows for reporting, stale-account triage, and access-review preparation.
This is original demonstration code using fictional data. It does not represent
production deployments, employer systems, or completed Microsoft Graph integration.

## What works today

| Workflow | Input | Output |
| --- | --- | --- |
| User reporting | Normalized users JSON | Selected identity fields in JSON |
| Stale-account triage | Users, threshold, evaluation timestamp | Classification for every user in JSON |
| Access-review preparation | Users and resource memberships | CSV worksheet with Pending decisions |

These scripts run offline. They do not authenticate, query a tenant, disable users,
remove memberships, or create Microsoft Entra access-review campaigns.
No dependencies or credentials are needed for the sample workflows.

## Structure

- `powershell/Invoke-EntraWorkflow.ps1`: PowerShell 7.2+ implementation.
- `python/entra_toolkit.py`: Python 3.9+ standard-library implementation.
- `tests/`: Python unit/integration tests and optional PowerShell parity tests.
- `samples/`: fictional fixtures and input schema.
- `practice/powershell/`, `practice/python/`: separate learning exercises.
- `labs/infrastructure/`: an explicitly unexecuted lab template.
- `docs/`: portfolio index and live-integration extension notes.

## Run with Python

From the repository root:

```sh
python3 python/entra_toolkit.py users --users samples/users.json --output reports/python-users.json
python3 python/entra_toolkit.py stale --users samples/users.json --days 90 --as-of 2026-09-07T00:00:00Z --output reports/python-stale.json
python3 python/entra_toolkit.py review --users samples/users.json --memberships samples/memberships.json --output reports/python-review.csv
python3 -m unittest discover -s tests -v
```

## Run with PowerShell

From the repository root, using `pwsh`:

```powershell
./powershell/Invoke-EntraWorkflow.ps1 -Workflow users -UsersPath samples/users.json -OutputPath reports/ps-users.json
./powershell/Invoke-EntraWorkflow.ps1 -Workflow stale -UsersPath samples/users.json -Days 90 -AsOf '2026-09-07T00:00:00Z' -OutputPath reports/ps-stale.json
./powershell/Invoke-EntraWorkflow.ps1 -Workflow review -UsersPath samples/users.json -MembershipsPath samples/memberships.json -OutputPath reports/ps-review.csv
```

Outputs are created exclusively; choose a new filename when rerunning. Reports
and private-data are ignored by Git. Keep actual exports in `private-data/`, never
in `samples/`. CSV strings that could become spreadsheet formulas are prefixed
with an apostrophe; this intentionally changes their presentation.

## Classification and review policy

Dates after the evaluation time, or a sign-in before creation, yield
`invalidTimeline`. Otherwise disabled users yield `disabled`; enabled users with
missing sign-in evidence yield `unknownActivity`; a successful sign-in at or before
the threshold yields `staleCandidate`; more recent activity yields `recentActivity`.
A stale candidate requires human investigation: service accounts, leave, exclusions,
data coverage and ownership are outside this starter's scope.

The review worksheet carries each supplied resource membership and assigned reviewer.
A human must verify the source, confirm the owner, and record a decision and rationale.
There is no decision import or enforcement implementation.

## Validation and next steps

Tests cover the cutoff boundary, disabled and unknown accounts, invalid timelines,
input validation, review joins, formula escaping, output protection, and empty inputs.
PowerShell parity tests run when `pwsh` is installed and are explicitly skipped otherwise.
See [validation results](docs/VALIDATION.md) for the actual local execution status.

For deliberate future work, see [integration notes](docs/LIVE-INTEGRATION.md).
See the [portfolio map](docs/PORTFOLIO.md) for related practice and lab structures.
