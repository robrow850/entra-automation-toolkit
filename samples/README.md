# Fictional fixtures

All identities and resources here are invented; example.com is used for sample addresses.
These are normalized offline inputs, not raw Microsoft Graph responses.

`users.json` is an array with unique string `id`, string `displayName`, string
`userPrincipalName`, boolean `accountEnabled`, and optional nullable timestamp fields
`createdDateTime` and `lastSuccessfulSignInDateTime`. Timestamps require a timezone.
A missing or null successful sign-in means unknown activity.

`memberships.json` contains unique user/resource pairs with string `userId`,
`resourceId`, `resourceName`, and `reviewer`. Every userId must exist in users.json.
Reviewers are placeholders requiring an actual resource owner's selection.

At 2026-09-07T00:00:00Z with 90 days, the expected statuses in input order are:
recentActivity, staleCandidate, unknownActivity, disabled, staleCandidate.
The exact cutoff is included in the stale candidate category.
