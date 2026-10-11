param([Parameter(Mandatory)][Alias("InstallDir")][string]$Root, [switch]$Plan, [Alias("CacheDir")][string]$CacheDirectory, [switch]$ConfigureCodex, [string]$CodexHome = (Join-Path $HOME '.codex'))
. "$PSScriptRoot/common.ps1"
$Root = Resolve-Root $Root
$source = Split-Path $PSScriptRoot
$dependencies = Get-Content -LiteralPath "$source/dependencies.json" -Raw | ConvertFrom-Json
if ($Plan) { @{ root=$Root; tools=$dependencies.tools; configureCodex=[bool]$ConfigureCodex; requires=@('PowerShell 7','Node 22+','Python 3.11+','.NET SDK 8+'); globalEnvironmentChanges=@() } | ConvertTo-Json -Depth 8; return }
if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'PowerShell 7 is required' }
if (Test-Path -LiteralPath $Root) { if (Get-ChildItem -LiteralPath $Root -Force) { throw 'Use an empty installation directory; existing files are never overwritten' } }
$node = (Get-Command node -ErrorAction Stop).Source
$python = (Get-Command python -ErrorAction Stop).Source
$npm = (Get-Command npm.cmd -ErrorAction Stop).Source
$dotnet = (Get-Command dotnet -ErrorAction Stop).Source
$nodeVersion = [version]((& $node --version).TrimStart('v'))
if (-not (($nodeVersion.Major -eq 22 -and $nodeVersion -ge [version]'22.19.0') -or ($nodeVersion.Major -eq 24 -and $nodeVersion -ge [version]'24.11.0') -or $nodeVersion.Major -ge 26)) { throw 'REA requires Node ^22.19.0, ^24.11.0 or >=26.0.0' }
Invoke-Checked $python @('-c','import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"')
if (-not ((& $dotnet --list-sdks) -match '^(8|9|[1-9][0-9])\.')) { throw '.NET SDK 8+ required' }
if (-not ((& $dotnet --list-runtimes) -match '^Microsoft.NETCore.App 8\.')) { throw '.NET 8 runtime required by ILSpy and Apktool launcher' }
New-Item -ItemType Directory -Force "$Root/downloads","$Root/temp","$Root/scripts","$Root/packages" | Out-Null
$saved = @{}
try {
 foreach ($key in @('TEMP','TMP','NUGET_PACKAGES','npm_config_cache','DOTNET_CLI_HOME')) { $saved[$key] = [Environment]::GetEnvironmentVariable($key,'Process'); [Environment]::SetEnvironmentVariable($key,"$Root/temp/$key",'Process'); New-Item -ItemType Directory -Force "$Root/temp/$key" | Out-Null }
 foreach ($key in @('DOTNET_CLI_TELEMETRY_OPTOUT','DOTNET_GENERATE_ASPNET_CERTIFICATE')) { $saved[$key] = [Environment]::GetEnvironmentVariable($key,'Process') }
 $env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
 $env:DOTNET_GENERATE_ASPNET_CERTIFICATE = 'false'
 foreach ($tool in $dependencies.tools) {
  if ($tool.archive -in @('npm','dotnet')) { continue }
  if ($tool.url -notmatch '^https://' -or $tool.sha256 -notmatch '^[a-fA-F0-9]{64}$') { throw "Unpinned dependency: $($tool.id)" }
  $name = [IO.Path]::GetFileName(([uri]$tool.url).AbsolutePath)
  $download = Join-Path "$Root/downloads" $name
  if ($CacheDirectory -and (Test-Path -LiteralPath (Join-Path $CacheDirectory $name))) { Copy-Item -LiteralPath (Join-Path $CacheDirectory $name) -Destination $download }
  else { Invoke-WebRequest -Uri $tool.url -OutFile $download -TimeoutSec 180 -MaximumRetryCount 1 -RetryIntervalSec 2 }
  if ((Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash -ne $tool.sha256) { throw "Checksum mismatch: $name" }
  if ($tool.archive -eq 'zip') { Expand-Archive -LiteralPath $download -DestinationPath "$Root/packages/$($tool.id)" }
  elseif ($tool.archive -eq 'jar') { $jarFolder = "$Root/packages/$($tool.id)/$($tool.folder)"; New-Item -ItemType Directory -Force $jarFolder | Out-Null; Copy-Item -LiteralPath $download -Destination (Join-Path $jarFolder $tool.executable) }
  else { throw "Unsupported archive type $($tool.archive)" }
 }
 $reaTool = $dependencies.tools | Where-Object id -eq 'rea'
 Invoke-Checked $npm @('install','--prefix',"$Root/packages/rea",'--no-audit','--no-fund','--fetch-retries=1','--fetch-timeout=180000',"rea-agents@$($reaTool.version)")
 $lock = Get-Content "$Root/packages/rea/package-lock.json" -Raw | ConvertFrom-Json -AsHashtable
 if ($lock.packages.'node_modules/rea-agents'.integrity -ne $reaTool.integrity) { throw 'REA npm integrity mismatch' }
 $ilspyTool = $dependencies.tools | Where-Object id -eq 'ilspy'
 '<configuration><packageSources><clear/><add key="nuget.org" value="https://api.nuget.org/v3/index.json"/></packageSources></configuration>' | Set-Content -LiteralPath "$Root/temp/NuGet.Config"
 Invoke-Checked $dotnet @('tool','install','ilspycmd','--tool-path',"$Root/packages/ilspy",'--version',$ilspyTool.version,'--configfile',"$Root/temp/NuGet.Config")
 $ilspyPackage = Get-ChildItem -LiteralPath "$Root/packages/ilspy/.store" -Recurse -Filter 'ilspycmd.nupkg' -File | Select-Object -First 1
 if (-not $ilspyPackage -or $ilspyTool.sha256 -notmatch '^[a-fA-F0-9]{64}$' -or (Get-FileHash -LiteralPath $ilspyPackage.FullName).Hash -ne $ilspyTool.sha256) { throw 'ILSpy package checksum mismatch' }
 Copy-Item -LiteralPath "$source/scripts/re-tool.py","$source/scripts/ExportStatic.java" -Destination "$Root/scripts"
 Copy-Item -LiteralPath "$source/scripts/common.ps1","$source/scripts/doctor.ps1","$source/scripts/configure.ps1","$source/scripts/uninstall.ps1" -Destination "$Root/scripts"
 New-Item -ItemType Directory -Force "$Root/bin" | Out-Null
 if ($Root -match '[%!"\r\n]' -or $python -match '[%!"\r\n]') { throw 'Unsupported Windows launcher path' }
 "@echo off`r`nchcp 65001 >nul`r`n`"$python`" `"%~dp0..\scripts\re-tool.py`" %*`r`n" | Set-Content -LiteralPath "$Root/bin/urimchain.cmd" -Encoding utf8NoBOM
 Copy-Item -LiteralPath "$source/skill/urimchain" -Destination "$Root/skill" -Recurse
 Copy-Item -LiteralPath "$source/scripts/apktool-launcher" -Destination "$Root/launcher-source" -Recurse
 Invoke-Checked $dotnet @('publish',"$Root/launcher-source/apktool-launcher.csproj",'-c','Release','-o',"$Root/apktool-launcher",'--self-contained','false')
 function Tool-Path([string]$id,[switch]$Folder) { $tool = $dependencies.tools | Where-Object id -eq $id; $base = "$Root/packages/$id"; if ($tool.folder) { $base = Join-Path $base $tool.folder }; if ($Folder) { return $base }; return Join-Path $base $tool.executable }
 $jdk = Tool-Path 'jdk' -Folder
 $ghidra = Tool-Path 'ghidra' -Folder
 $jadxFolder = Tool-Path 'jadx' -Folder
 $manifest = @{jdk=$jdk; ghidra=$ghidra; jadx_jar="$jadxFolder/lib/jadx-$(( $dependencies.tools | Where-Object id -eq 'jadx').version)-all.jar"; apktool=(Tool-Path 'apktool'); ilspy="$Root/packages/ilspy/ilspycmd.exe"; node=$node; python=$python; rea="$Root/packages/rea/node_modules/rea-agents/scripts/rea.mjs"; rea_env=@{JAVA_HOME=$jdk;GHIDRA_INSTALL_DIR=$ghidra;REA_JADX_MCP_JAR=(Tool-Path 'bridge');REA_APKTOOL_COMMAND="$Root/apktool-launcher/apktool-launcher.exe";TEMP="$Root/temp";TMP="$Root/temp"}}
 $manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath "$Root/toolchain.json" -Encoding utf8
} finally {
 foreach ($key in $saved.Keys) { [Environment]::SetEnvironmentVariable($key,$saved[$key],'Process') }
 # Record partial installations too so a failed download/build can be safely removed.
 @{product='Urimchain';version='0.1.0';root=$Root;files=@(Get-ChildItem -LiteralPath $Root -File -Recurse | Where-Object Name -ne 'urimchain-install.json' | ForEach-Object { @{path=[IO.Path]::GetRelativePath($Root,$_.FullName);sha256=(Get-FileHash -LiteralPath $_.FullName).Hash} })} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath "$Root/urimchain-install.json" -Encoding utf8
}
if ($ConfigureCodex) { & "$PSScriptRoot/configure.ps1" -Root $Root -CodexHome $CodexHome }
& "$PSScriptRoot/doctor.ps1" -Root $Root
