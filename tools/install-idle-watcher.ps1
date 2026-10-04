<#
Installs the iTantra idle watcher (tools/idle_watcher.py) as a hidden Scheduled Task for the current user.

    powershell -NoProfile -ExecutionPolicy Bypass -File tools\install-idle-watcher.ps1 -Repo <lead folder> -Clone <watch clone path>
    powershell -NoProfile -ExecutionPolicy Bypass -File tools\install-idle-watcher.ps1 -Uninstall

-ExecutionPolicy Bypass applies to this one process only; the machine's policy is not changed.
#>
param(
    [string]$Repo,
    [string]$Clone,
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
$TaskName = 'itantra-idle-watcher'

if ($Uninstall) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed scheduled task $TaskName."
    } else {
        Write-Host "Scheduled task $TaskName is not installed."
    }
    exit 0
}

if (-not $Repo -or -not $Clone) { throw 'Give -Repo <lead folder> and -Clone <watch clone path> (or -Uninstall).' }
$Repo = (Resolve-Path $Repo).Path
$Script = Join-Path $Repo 'tools\idle_watcher.py'
if (-not (Test-Path $Script)) { throw "Not found: $Script" }

# 1. Dedicated read-only clone of the same GitHub repo.
if (-not (Test-Path (Join-Path $Clone '.git'))) {
    $url = (& git -C $Repo remote get-url origin).Trim()
    if (-not $url) { throw "Could not read the origin URL of $Repo" }
    Write-Host "Cloning $url into $Clone ..."
    & git clone -q $url $Clone
    if ($LASTEXITCODE -ne 0) { throw 'git clone failed' }
} else {
    Write-Host "Clone already exists: $Clone"
}
$Clone = (Resolve-Path $Clone).Path

# 2. "The film has unfinished work" flag.
$local = Join-Path $Repo 'local'
New-Item -ItemType Directory -Force -Path $local | Out-Null
$flag = Join-Path $local 'watcher-active'
if (-not (Test-Path $flag)) { New-Item -ItemType File -Path $flag | Out-Null }
$out = Join-Path $local 'worker-status.md'

# 3. pythonw.exe next to python on PATH.
$py = (Get-Command python -ErrorAction SilentlyContinue | Where-Object { $_.Source -notlike '*WindowsApps*' } | Select-Object -First 1)
if (-not $py) { throw 'python was not found on PATH (the WindowsApps stub does not count).' }
$pythonw = Join-Path (Split-Path $py.Source) 'pythonw.exe'
if (-not (Test-Path $pythonw)) { throw "pythonw.exe not found next to $($py.Source)" }

# 4. Scheduled task: at logon, hidden, no time limit, restart 3 times 1 min apart.
$argLine = "`"$Script`" --loop --clone `"$Clone`" --out `"$out`" --active-flag `"$flag`""
$action = New-ScheduledTaskAction -Execute $pythonw -Argument $argLine -WorkingDirectory $Repo
$user = "$env:USERDOMAIN\$env:USERNAME"
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -Hidden -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal `
    -Settings $settings -Description 'iTantra: pings ntfy when a worker idles while work is waiting' | Out-Null

# 5. Start it now.
Start-ScheduledTask -TaskName $TaskName
Write-Host "Installed and started $TaskName."
Write-Host "Status file: $out  (log: $out.log)"
Write-Host "Remove the flag file $flag when the film has no unfinished work."
