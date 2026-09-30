param([string]$TaskDir = $PSScriptRoot)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $TaskDir '../..')).Path
$outRoot = Join-Path $repo 'local/renders/scene2/narration'
New-Item -ItemType Directory -Force $outRoot | Out-Null

$lines = [ordered]@{
    N1 = "Let's see how far that message actually has to travel."
    N2 = "But how did that happen? Bluetooth doesn't reach that far."
    N3 = "And that's how it gets there."
    N4 = "His reply comes back the same way."
}
$voice = New-Object -ComObject SAPI.SpVoice
$installed = @($voice.GetVoices() | ForEach-Object { $_ })
$chosen = @($installed | Where-Object { $_.GetDescription() -match 'English \(India\)' } | Select-Object -First 3)
if (-not $chosen) { $chosen = @($installed | Where-Object { $_.GetDescription() -match 'English \((United States|United Kingdom)\)' } | Select-Object -First 3) }
if (-not $chosen) { throw 'No installed English SAPI voice is available.' }

$manifest = [ordered]@{}
foreach ($token in $chosen) {
    $name = ($token.GetDescription() -replace '^Microsoft\s+', '' -replace '\s+Desktop.*$', '' -replace '\s+-.*$', '').ToLowerInvariant()
    $dir = Join-Path $outRoot $name
    New-Item -ItemType Directory -Force $dir | Out-Null
    $voice.Voice = $token
    $voice.Rate = -1
    $manifest[$name] = [ordered]@{}
    foreach ($id in $lines.Keys) {
        $raw = Join-Path $dir "$id.raw.wav"
        $final = Join-Path $dir "$id.wav"
        $stream = New-Object -ComObject SAPI.SpFileStream
        try {
            $stream.Open($raw, 3, $false)
            $voice.AudioOutputStream = $stream
            [void]$voice.Speak($lines[$id], 0)
        } finally {
            $stream.Close()
        }
        $filter = 'silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB,areverse,adelay=30,apad=pad_dur=0.03,loudnorm=I=-18:TP=-2:LRA=7'
        & ffmpeg -hide_banner -loglevel error -y -i $raw -af $filter -ar 48000 -ac 1 -c:a pcm_s24le $final
        if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed for $name/$id" }
        Remove-Item -LiteralPath $raw
        $duration = & ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $final
        if ($LASTEXITCODE -ne 0) { throw "ffprobe failed for $name/$id" }
        $manifest[$name][$id] = [ordered]@{ text = $lines[$id]; duration_s = [math]::Round([double]::Parse($duration, [cultureinfo]::InvariantCulture), 3) }
    }
}
$manifest['recommended_voice'] = ($manifest.Keys | Select-Object -First 1)
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $TaskDir 'narration.json')
