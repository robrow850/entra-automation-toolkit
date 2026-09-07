# Validation record

Executed locally on 2026-09-07 using Python 3.9.6 and PowerShell 7.6.5:

`python3 -m unittest discover -s tests -v`

Result: all 13 tests passed, none skipped. All fixtures are fictional.
The tests execute all three Python and PowerShell command-line workflows,
compare their sample outputs, and verify existing outputs cannot be overwritten.

Execution exposed and resolved automatic JSON timestamp conversion in newer
PowerShell and timestamp precision compatibility with Python 3.9.
PowerShell versions other than 7.6.5 were not execution-tested.
No live tenant, Microsoft Graph, or infrastructure deployment was tested.
