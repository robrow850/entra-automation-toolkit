# Future live integration — not implemented

The delivered code consumes normalized local JSON. The following are design tasks,
not working features or executable authentication instructions.

1. Choose a disposable test tenant and an authorized read-only data source.
2. Consult current Microsoft documentation for permissions, licensing, roles,
   available sign-in fields, retention, and API limits before implementing a collector.
3. Implement authentication using a supported identity library; keep credentials
   outside this repository and never log tokens or personal data.
4. Implement pagination, bounded retries, throttling handling and explicit failure
   reporting. Capture collection time and evidence coverage.
5. Normalize the chosen successful sign-in field into lastSuccessfulSignInDateTime.
   Never substitute attempted sign-in activity or interpret missing history as never used.
6. Add mocked collector tests before using fictional test-tenant identities.
7. Treat campaign creation and decision enforcement as separate future features with
   scope validation, exclusions, explicit approval, audit records and recovery planning.

Safe placeholder interface: a future collector may write users.json and memberships.json
in the documented schema under private-data/. No collector is currently supplied.
