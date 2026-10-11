param([Parameter(Mandatory)][Alias("InstallDir")][string]$Root, [string]$CodexHome = (Join-Path $HOME '.codex'))
. "$PSScriptRoot/common.ps1"
$Root = Resolve-Root $Root
$null = Read-Installation $Root
if (Test-Path -LiteralPath "$Root/urimchain-config.json") { throw 'This installation is already registered; preserve its existing registration' }
$config = Get-Content -LiteralPath "$Root/toolchain.json" -Raw | ConvertFrom-Json
foreach ($value in @($config.node,$config.rea)) { if ($value -match "['\r\n]") { throw 'Unsupported TOML command path' } }
$path = Join-Path $CodexHome 'config.toml'
$text = if (Test-Path -LiteralPath $path) { [IO.File]::ReadAllText($path) } else { '' }
New-Item -ItemType Directory -Force "$Root/temp" | Out-Null
$check = Join-Path "$Root/temp" (([guid]::NewGuid().ToString()) + '.toml')
try {
 [IO.File]::WriteAllText($check,$text)
 $registrationState = & (Get-Command python -ErrorAction Stop).Source -c 'import sys,tomllib; data=tomllib.load(open(sys.argv[1], "rb")); print("present" if "urimchain" in data.get("mcp_servers", {}) else "absent")' $check
 if ($LASTEXITCODE -ne 0) { throw 'Invalid existing TOML configuration retained' }
 if ($registrationState -eq 'present') { throw 'Existing urimchain MCP configuration retained; choose another Codex home or remove it manually' }
} finally { if (Test-Path -LiteralPath $check) { Remove-Item -LiteralPath $check } }
$skill = Join-Path $CodexHome 'skills/urimchain'
if (Test-Path -LiteralPath $skill) { throw 'Existing urimchain Skill retained' }
New-Item -ItemType Directory -Force $CodexHome | Out-Null
$backup = Join-Path $Root ('backups/config-' + (Get-Date -Format 'yyyyMMddHHmmssffff') + '.toml')
New-Item -ItemType Directory -Force (Split-Path $backup) | Out-Null
[IO.File]::WriteAllText($backup, $text)
$block = "`n# Urimchain managed block`n[mcp_servers.urimchain]`ncommand = '$($config.node)'`nargs = ['$($config.rea)', 'mcp']`n[mcp_servers.urimchain.env]`n"
foreach ($entry in $config.rea_env.PSObject.Properties) { if ($entry.Value -match "['\r\n]") { throw 'Unsupported TOML environment value' }; $block += "$($entry.Name) = '$($entry.Value)'`n" }
try {
 [IO.File]::WriteAllText($check,$text + $block)
 Invoke-Checked (Get-Command python -ErrorAction Stop).Source @('-c','import sys,tomllib; tomllib.load(open(sys.argv[1], "rb"))',$check)
} finally { if (Test-Path -LiteralPath $check) { Remove-Item -LiteralPath $check } }
Copy-Item -LiteralPath "$Root/skill" -Destination $skill -Recurse
[IO.File]::WriteAllText($path, $text + $block)
@{ config = $path; block = $block; skill = $skill; skillHashes = @(Get-ChildItem $skill -File -Recurse | ForEach-Object { @{path=$_.FullName;sha256=(Get-FileHash $_.FullName).Hash} }); backup = $backup } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath "$Root/urimchain-config.json" -Encoding utf8
Write-Output 'Codex configuration appended and backed up. Reconnect MCP to load it.'
