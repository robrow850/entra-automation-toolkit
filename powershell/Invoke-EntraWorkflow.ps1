#requires -Version 7.2
<#
.SYNOPSIS
Offline user reporting, stale-account triage, and human access-review preparation.
.DESCRIPTION
Accepts normalized JSON exports. No Graph connection or tenant mutations occur.
Missing sign-in evidence is unknown, not proof an account has never signed in.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('users', 'stale', 'review')][string]$Workflow,
    [Parameter(Mandatory)][string]$UsersPath,
    [string]$MembershipsPath,
    [ValidateRange(1, 2147483647)][int]$Days = 90,
    [DateTimeOffset]$AsOf = [DateTimeOffset]::UtcNow,
    [Parameter(Mandatory)][string]$OutputPath
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertTo-UtcTimestamp([string]$Value) {
    if ($Value -notmatch '(Z|[+-]\d{2}:\d{2})$') { throw 'Timestamp must include a timezone' }
    return [DateTimeOffset]::Parse($Value, [Globalization.CultureInfo]::InvariantCulture).ToUniversalTime()
}
function Read-JsonArray([string]$Path) {
    $raw = Get-Content -LiteralPath $Path -Raw
    if (-not $raw.TrimStart().StartsWith('[')) { throw 'Expected a JSON array' }
    # Hashtable access lets optional timestamp fields be absent.
    # Newer PowerShell versions convert JSON timestamps automatically. Preserve
    # strings for explicit timezone validation and parity with the Python reader.
    $jsonOptions = @{ AsHashtable = $true }
    if ((Get-Command ConvertFrom-Json).Parameters.ContainsKey('DateKind')) {
        $jsonOptions.DateKind = 'String'
    }
    return ,@($raw | ConvertFrom-Json @jsonOptions)
}
function Protect-CsvCell($Value) {
    if ($Value -is [string] -and $Value -match '^\s*[=+@-]') { return "'$Value" }
    return $Value
}

$users = Read-JsonArray $UsersPath
$byId = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
foreach ($user in $users) {
    if ($user -isnot [Collections.IDictionary]) { throw 'Each user must be an object' }
    foreach ($field in @('id', 'displayName', 'userPrincipalName')) {
        if ($user[$field] -isnot [string] -or [string]::IsNullOrWhiteSpace($user[$field])) {
            throw "Missing or invalid $field"
        }
    }
    if ($byId.ContainsKey($user.id)) { throw "Duplicate user id: $($user.id)" }
    if ($user.accountEnabled -isnot [bool]) { throw 'accountEnabled must be a JSON boolean' }
    foreach ($field in @('createdDateTime', 'lastSuccessfulSignInDateTime')) {
        if ($null -ne $user[$field]) {
            if ($user[$field] -isnot [string] -or $user[$field] -eq '') { throw "Invalid $field" }
            $null = ConvertTo-UtcTimestamp $user[$field]
        }
    }
    $byId.Add($user.id, $user)
}

$rows = @(switch ($Workflow) {
    'users' {
        foreach ($user in $users) {
            [pscustomobject][ordered]@{
                id = $user.id; displayName = $user.displayName
                userPrincipalName = $user.userPrincipalName; accountEnabled = $user.accountEnabled
                createdDateTime = $user.createdDateTime
                lastSuccessfulSignInDateTime = $user.lastSuccessfulSignInDateTime
            }
        }
    }
    'stale' {
        $cutoff = $AsOf.AddDays(-$Days)
        foreach ($user in $users) {
            $last = $null; $created = $null
            if ($user.lastSuccessfulSignInDateTime) { $last = ConvertTo-UtcTimestamp $user.lastSuccessfulSignInDateTime }
            if ($user.createdDateTime) { $created = ConvertTo-UtcTimestamp $user.createdDateTime }
            $status = if (($null -ne $last -and $last -gt $AsOf) -or
                ($null -ne $created -and $created -gt $AsOf) -or
                ($null -ne $last -and $null -ne $created -and $last -lt $created)) { 'invalidTimeline' }
                elseif (-not $user.accountEnabled) { 'disabled' }
                elseif ($null -eq $last) { 'unknownActivity' }
                elseif ($last -le $cutoff) { 'staleCandidate' }
                else { 'recentActivity' }
            [pscustomobject][ordered]@{
                id = $user.id; userPrincipalName = $user.userPrincipalName; status = $status
                lastSuccessfulSignInDateTime = $user.lastSuccessfulSignInDateTime
                asOf = $AsOf.ToString("yyyy-MM-dd'T'HH:mm:ss.ffffffzzz"); thresholdDays = $Days
            }
        }
    }
    'review' {
        if (-not $MembershipsPath) { throw 'review requires MembershipsPath' }
        $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        foreach ($member in (Read-JsonArray $MembershipsPath)) {
            if ($member -isnot [Collections.IDictionary]) { throw 'Each membership must be an object' }
            foreach ($field in @('userId', 'resourceId', 'resourceName', 'reviewer')) {
                if ($member[$field] -isnot [string] -or [string]::IsNullOrWhiteSpace($member[$field])) {
                    throw "Missing or invalid membership $field"
                }
            }
            if (-not $byId.ContainsKey($member.userId)) { throw 'Membership references an unknown user' }
            $pair = ConvertTo-Json -InputObject @($member.userId, $member.resourceId) -Compress
            if (-not $seen.Add($pair)) { throw 'Duplicate user/resource membership' }
            [pscustomobject][ordered]@{
                userId = Protect-CsvCell $member.userId
                userPrincipalName = Protect-CsvCell $byId[$member.userId].userPrincipalName
                resourceId = Protect-CsvCell $member.resourceId
                resourceName = Protect-CsvCell $member.resourceName
                reviewer = Protect-CsvCell $member.reviewer
                decision = 'Pending'; justification = ''
            }
        }
    }
})

$fullPath = [IO.Path]::GetFullPath($OutputPath)
$null = [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($fullPath))
# CreateNew prevents accidental replacement of an input file or earlier report.
$stream = [IO.File]::Open($fullPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
$writer = [IO.StreamWriter]::new($stream, [Text.UTF8Encoding]::new($false))
try {
    if ($Workflow -eq 'review') {
        if ($rows.Count -eq 0) {
            $writer.WriteLine('"userId","userPrincipalName","resourceId","resourceName","reviewer","decision","justification"')
        } else { $rows | ConvertTo-Csv -NoTypeInformation | ForEach-Object { $writer.WriteLine($_) } }
    } else { $writer.WriteLine((ConvertTo-Json -InputObject $rows -Depth 8)) }
} finally { $writer.Dispose() }
