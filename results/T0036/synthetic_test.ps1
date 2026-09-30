# Run from the repo root. All synthetic media is removed before exit.
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$fixtures = Join-Path $PSScriptRoot 'synthetic_inputs'
$output = Join-Path $PSScriptRoot 'synthetic_output'
New-Item -ItemType Directory -Force $fixtures, $output | Out-Null

function Make-Voice($name, $seconds, $lead, $tail, $codec) {
    $file = Join-Path $fixtures $name
    $filter = "anoisesrc=d=$($seconds):c=pink:r=48000,highpass=f=180,lowpass=f=3200,tremolo=f=4:d=0.8,volume=0.25,adelay=$($lead),apad=pad_dur=$($tail)"
    & ffmpeg -v error -y -f lavfi -i $filter -c:a $codec $file
    if ($LASTEXITCODE -ne 0) { throw "FFmpeg failed to make $name" }
}

try {
    # The clipped N1_a should lose to N1_b. N2 has long edge silences.
    & ffmpeg -v error -y -f lavfi -i 'aevalsrc=1:d=3:s=48000' -c:a pcm_s16le (Join-Path $fixtures 'N1_a.wav')
    if ($LASTEXITCODE -ne 0) { throw 'FFmpeg failed to make clipped N1' }
    Make-Voice 'N1_b.wav' 3.0 300 0.3 pcm_s16le
    Make-Voice 'n2.m4a' 3.8 1200 1.1 aac
    Make-Voice 'N3.mp3' 1.5 200 0.3 libmp3lame
    Make-Voice 'N5.aac' 3.0 250 0.4 aac
    Make-Voice 'N6.ogg' 8.0 200 0.3 libvorbis

    Push-Location $repo
    try {
        & python film/narration/prep.py --input $fixtures --out $output --no-switch
        if ($LASTEXITCODE -ne 0) { throw "prep.py exited $LASTEXITCODE" }
    } finally { Pop-Location }

    $report = Get-Content (Join-Path $output 'report.json') -Raw | ConvertFrom-Json
    if ($report.lines.N1.chosen -ne 'N1_b.wav') { throw 'N1 did not reject the clipped take' }
    if ($report.missing.Count -ne 0) { throw 'A line is missing' }
    if (-not (($report.lines.N6.takes | Where-Object take -eq 'N6.ogg').over_max)) { throw 'N6 should remain over max after the 6% cap' }
    if ($report.switched) { throw 'Test mode changed the film voice switch' }
    foreach ($line in @('N1','N2','N3','N5','N6')) {
        if (-not (Test-Path (Join-Path $output "$line.wav"))) { throw "$line output is missing" }
    }
    Write-Output 'PASS: five lines, clipped-take rejection, long-silence trimming, 6% cap, and no voice switch.'
    $report.lines | ConvertTo-Json -Depth 5
} finally {
    # Both directories are fixed children of this result folder. Remove files,
    # then the empty directories; do not recursively remove computed paths.
    Get-ChildItem -LiteralPath $fixtures -File -ErrorAction SilentlyContinue | Remove-Item
    Get-ChildItem -LiteralPath $output -File -ErrorAction SilentlyContinue | Remove-Item
    Remove-Item -LiteralPath $fixtures -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $output -ErrorAction SilentlyContinue
}
