param (
    [string]$command
)

# Log start time
$startTime = Get-Date
Write-Host "Starting command: $command"

# Start the process and store it in a variable
$process = Start-Process cmd -ArgumentList "/c $command" -NoNewWindow -PassThru -RedirectStandardOutput "output.log" -RedirectStandardError "error.log"

# Initialize counters
$earlyStopCount = 0

# Wait for the process to finish or check for "Singular matrix" or "The program has been early stopped!" errors
while (!$process.HasExited) {
    Start-Sleep -Seconds 60 # Check every 60 seconds
    $output = Get-Content "output.log" -ErrorAction SilentlyContinue
    if ($output -match "Singular matrix.") {
        Write-Host "Singular matrix error detected. Terminating the process..."
        Get-Process -Name standard | Stop-Process -Force
        Start-Sleep -Seconds 5
        break
    } elseif ($output -match "The program has been early stopped!") {
        $earlyStopCount++
        Write-Host "Early stop detected. Count: $earlyStopCount"
        if ($earlyStopCount -ge 2) {
            Write-Host "Early stop detected twice. The process might be stuck. Terminating the process..."
            Get-Process -Name standard | Stop-Process -Force
            Start-Sleep -Seconds 5
            break
        }
    }
}

# Log end time
$endTime = Get-Date
Write-Host "Command completed at $endTime"

# Check if the process exited with an error
if ($process.ExitCode -ne 0) {
    Write-Host "Command exited with an error."
} else {
    Write-Host "Task completed successfully."
}
