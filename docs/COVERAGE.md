# Email plan coverage — September 7, 2026

Every project idea from the development-plan email has a starter implementation or
an executable configuration/UI example. This is completion of the starter build,
not completion of production integrations, Windows validation or Azure deployment.
The email's powershell-labs and python-labs categories map to the already-created
powershell-automation and python-automation repositories; no duplicate repos were created.

| Area | Email idea | Delivered scope and limits |
| --- | --- | --- |
| PowerShell | [Entra user lifecycle](https://github.com/robrow850/powershell-automation/tree/main/entra-id) | Runnable local create/update/disable simulation, group/license assignments, WhatIf; no Graph writes |
| PowerShell | [AD health check](https://github.com/robrow850/powershell-automation/tree/main/active-directory) | Runnable evaluator of normalized DC, replication, DNS, stale-object, password-policy and FSMO evidence; no live collector |
| PowerShell | [M365 license auditor](https://github.com/robrow850/powershell-automation/tree/main/microsoft-graph) | Runnable fixture audit, exception detection, CSV/HTML; no live license collection |
| PowerShell | [Group membership analyzer](https://github.com/robrow850/powershell-automation/tree/main/active-directory) | Runnable nested traversal, cycles, privileged/unresolved members and depth bound |
| PowerShell | [Exchange mailbox auditor](https://github.com/robrow850/powershell-automation/tree/main/exchange-online) | Runnable forwarding, delegate, FullAccess/shared-mailbox review from fixtures |
| PowerShell | [Parallel automation framework](https://github.com/robrow850/powershell-automation/tree/main/automation) | Runnable sample jobs with bounded runspaces, retries, progress and structured results |
| PowerShell | [WPF administration console](https://github.com/robrow850/powershell-automation/tree/main/powershell-gui) | Windows-only UI with asynchronous worker; syntax and platform guard checked; Windows UI unverified |
| PowerShell | [Graph wrapper module](https://github.com/robrow850/powershell-automation/tree/main/microsoft-graph) | Fixture mode plus live GET implementation accepting externally obtained secure token; live path unverified |
| Python | [REST API client](https://github.com/robrow850/python-automation/tree/main/api-automation) | requests GET with timeout, bounded HTTP retries and no redirects; mocked transport tests |
| Python | [Async API client](https://github.com/robrow850/python-automation/tree/main/api-automation) | aiohttp GET with bounded concurrency and timeout; mocked transport tests |
| Python | [System inventory](https://github.com/robrow850/python-automation/tree/main/system-admin) | Runnable local OS/architecture/runtime inventory; not a remote Windows collector |
| Python | [Log parser and anomaly finder](https://github.com/robrow850/python-automation/blob/main/labtools.py) | Runnable JSONL parser, WARN/ERROR candidates and malformed-line reporting |
| Python | [CSV/JSON transformation](https://github.com/robrow850/python-automation/tree/main/file-processing) | Runnable validated CSV-to-JSON conversion |
| Python | [Graph client](https://github.com/robrow850/python-automation/tree/main/api-automation) | Fixture mode plus users GET with bounded trusted-host pagination and external token; no tenant validation |
| Python | [HTML reporting](https://github.com/robrow850/python-automation/tree/main/reporting) | Runnable escaped HTML table with actual fictional sample report |
| Python | [SQL reporting](https://github.com/robrow850/python-automation/tree/main/reporting) | Runnable parameterized in-memory SQLite report |
| Python | [File migration and verification](https://github.com/robrow850/python-automation/tree/main/file-processing) | Runnable plan-first copy to new destination, SHA-256 verification and source preservation |
| Python | [Configuration drift detector](https://github.com/robrow850/python-automation/tree/main/system-admin) | Runnable recursive JSON comparison, distinguishing missing/null and types |
| Python | [Administrative CLI](https://github.com/robrow850/python-automation/blob/main/lab_cli.py) | Runnable argparse commands, structured events and nonzero failure exit |
| Paired languages | [System inventory pair](https://github.com/robrow850/python-automation/tree/main/powershell-to-python/system_inventory) | Both implementations supplied; language-specific runtime fields |
| Paired languages | [REST API pair](https://github.com/robrow850/python-automation/tree/main/powershell-to-python/rest_api) | Both implementations supplied; fixture parity tested |
| Paired languages | [Log parser pair](https://github.com/robrow850/python-automation/tree/main/powershell-to-python/log_parser) | Both implementations supplied; fixture parity tested |
| Infrastructure | [Terraform](https://github.com/robrow850/infrastructure-labs/tree/main/terraform) | Local terraform_data and Azure resource-group configurations; fmt/init/validate passed in GitHub |
| Infrastructure | [GitHub Actions / CI](https://github.com/robrow850/infrastructure-labs/tree/main/github-actions) | Active validation workflows in the three supporting repositories; no deployment credentials |
| Infrastructure | [Azure automation](https://github.com/robrow850/infrastructure-labs/tree/main/azure) | Bicep alternative and read-only subscription preflight; no deployed resources |
| Flagship | [Entra reporting, stale accounts and access reviews](https://github.com/robrow850/entra-automation-toolkit) | Both languages have offline normalized-data workflows; 13 local tests pass; no live tenant writes |

## Verified evidence

- Entra toolkit: 13 local tests passed on Python 3.9.6 and PowerShell 7.6.5.
- Python labs: 20 local tests passed, including mocked transport and paired-language checks.
- PowerShell labs: offline assertions passed for all console projects; WPF syntax/platform guard checked.
- [PowerShell GitHub checks](https://github.com/robrow850/powershell-automation/actions/runs/34143055110): passed.
- [Python GitHub checks](https://github.com/robrow850/python-automation/actions/runs/34143146512): passed.
- [Terraform GitHub checks](https://github.com/robrow850/infrastructure-labs/actions/runs/34143208187): both local and Azure configuration validation passed.

## Remaining environment-dependent work

Live AD/Exchange collectors, tenant writes, OAuth acquisition/refresh, permission and
licensing verification, actual Windows WPF interaction/screenshots, and authenticated
Azure plan/apply/cleanup are not claimed as completed. Lab datasets are fictional.
The real environments and actual evidence must be supplied before those projects
can be represented as deployed or production-ready.
