#requires -Version 7.2
<# .SYNOPSIS
Read-only immediate-directory inventory; does not read file contents.
#>
[CmdletBinding()]
param([Parameter(Mandatory)][string]$Directory)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Directory -PathType Container)) { throw 'Directory must exist' }
Get-ChildItem -LiteralPath $Directory -File -Force |
    Where-Object { -not $_.LinkType } | Sort-Object Name |
    Select-Object Name, @{Name='Bytes'; Expression={$_.Length}}
