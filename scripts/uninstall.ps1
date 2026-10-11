param([Parameter(Mandatory)][Alias("InstallDir")][string]$Root, [switch]$Plan)
. "$PSScriptRoot/common.ps1"
$Root = Resolve-Root $Root
$record = Read-Installation $Root
$owned = @($record.files)
foreach ($entry in $owned) { $target = [IO.Path]::GetFullPath((Join-Path $Root $entry.path)); if (-not $target.StartsWith($Root + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Ownership path escapes root' }; if ((Test-Path -LiteralPath $target) -and (Get-FileHash -LiteralPath $target).Hash -ne $entry.sha256) { throw "Modified owned file retained: $target" } }
if ($Plan) { $owned.path; return }
if (Test-Path -LiteralPath "$Root/urimchain-config.json") {
 $registration = Get-Content "$Root/urimchain-config.json" -Raw | ConvertFrom-Json
 if (Test-Path -LiteralPath $registration.config) { $text = [IO.File]::ReadAllText($registration.config); if ($text.Contains($registration.block)) { [IO.File]::WriteAllText($registration.config,$text.Replace($registration.block,'')) } else { Write-Warning 'Changed MCP block retained' } }
 foreach ($entry in $registration.skillHashes) { $skillFile = [IO.Path]::GetFullPath($entry.path); $skillRoot = [IO.Path]::GetFullPath($registration.skill).TrimEnd('\','/'); if (-not $skillFile.StartsWith($skillRoot + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Skill ownership path escapes root' }; if ((Test-Path -LiteralPath $skillFile) -and (Get-FileHash -LiteralPath $skillFile).Hash -eq $entry.sha256) { Remove-Item -LiteralPath $skillFile } }
 Remove-Item -LiteralPath "$Root/urimchain-config.json"
}
foreach ($entry in $owned) { $target = Join-Path $Root $entry.path; if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target } }
Remove-Item -LiteralPath "$Root/urimchain-install.json"
Get-ChildItem -LiteralPath $Root -Directory -Recurse | Sort-Object { $_.FullName.Length } -Descending | ForEach-Object { if (-not (Get-ChildItem -LiteralPath $_.FullName -Force)) { Remove-Item -LiteralPath $_.FullName } }
Write-Output 'Owned files removed. User files, analysis results and backups retained.'
