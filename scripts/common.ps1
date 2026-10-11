$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
function Invoke-Checked {
 param([string]$Command, [string[]]$Arguments)
 $start = [Diagnostics.ProcessStartInfo]::new($Command)
 $start.UseShellExecute = $false
 if ($Command -match '\.(cmd|bat)$') {
  foreach ($argument in @($Command) + $Arguments) { if ($argument -match '[%!"\r\n]') { throw 'Unsupported Windows batch argument' } }
  $start.FileName = $env:ComSpec
  $start.Arguments = '/d /s /c "' + ((@($Command) + $Arguments | ForEach-Object { '"' + $_ + '"' }) -join ' ') + '"'
 } else { foreach ($argument in $Arguments) { $start.ArgumentList.Add($argument) } }
 $process = [Diagnostics.Process]::Start($start)
 try { if (-not $process.WaitForExit(600000)) { $process.Kill($true); $process.WaitForExit(); throw "$Command timed out after 10 minutes" }; if ($process.ExitCode -ne 0) { throw "$Command failed ($($process.ExitCode))" } } finally { $process.Dispose() }
}
function Resolve-Root { param([string]$Root) $value = [IO.Path]::GetFullPath($Root); if ($value -eq [IO.Path]::GetPathRoot($value)) { throw 'A drive root is not an installation directory' }; return $value.TrimEnd('\','/') }
function Read-Installation { param([string]$Root) $Root = Resolve-Root $Root; $record = Get-Content -LiteralPath (Join-Path $Root 'urimchain-install.json') -Raw | ConvertFrom-Json; if ($record.product -ne 'Urimchain' -or $record.root -ne $Root) { throw 'Installation ownership record does not match' }; return $record }
