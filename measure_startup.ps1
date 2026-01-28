$sw = [Diagnostics.Stopwatch]::StartNew()
Write-Host "Starting yt_abstract.exe..."
# Assumes the script is run from project root and exe is in dist/yt_abstract/
$process = Start-Process -FilePath ".\dist\yt_abstract\yt_abstract.exe" -PassThru -NoNewWindow

# Poll for API availability
do {
    Start-Sleep -Milliseconds 500
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/app_icon.png" -Method HEAD -TimeoutSec 1 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $sw.Stop()
            Write-Host "Success! Startup time: $($sw.Elapsed.TotalSeconds) seconds"
            Stop-Process -Id $process.Id -Force
            exit 0
        }
    }
    catch {
        # Ignore errors and keep polling
    }
} while ($sw.Elapsed.TotalSeconds -lt 120)

$sw.Stop()
Write-Host "Timeout or Failure. Time elapsed: $($sw.Elapsed.TotalSeconds) seconds"
if (-not $process.HasExited) {
    Stop-Process -Id $process.Id -Force
}
exit 1
