param([Parameter(Mandatory)][Alias("InstallDir")][string]$Root)
. "$PSScriptRoot/common.ps1"
$Root = Resolve-Root $Root
$null = Read-Installation $Root
$config = Get-Content -LiteralPath "$Root/toolchain.json" -Raw | ConvertFrom-Json
foreach ($key in 'jdk','ghidra','jadx_jar','apktool','ilspy','node','rea') { if (-not (Test-Path -LiteralPath $config.$key)) { throw "Missing $key" } }
$saved = @{}
try {
 foreach ($entry in $config.rea_env.PSObject.Properties) { $saved[$entry.Name] = [Environment]::GetEnvironmentVariable($entry.Name,'Process'); [Environment]::SetEnvironmentVariable($entry.Name,$entry.Value,'Process') }
 Invoke-Checked "$($config.jdk)/bin/java.exe" @('-version')
 Invoke-Checked "$($config.jdk)/bin/java.exe" @('-cp',$config.jadx_jar,'jadx.cli.JadxCLI','--version')
 Invoke-Checked "$($config.jdk)/bin/java.exe" @('-jar',$config.apktool,'--version')
 Invoke-Checked $config.ilspy @('--version')
 Invoke-Checked $config.node @($config.rea,'doctor','--provider','ghidra','--json')
} finally { foreach ($key in $saved.Keys) { [Environment]::SetEnvironmentVariable($key,$saved[$key],'Process') } }
Write-Output 'Doctor passed tool invocation. Real analysis requires the separate integration tests.'
