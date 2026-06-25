# scripts/stop_jarvis.ps1

Write-Host "Stopping Project Jarvis..." -ForegroundColor Cyan


# ============================================================
# STOP JARVIS SERVERS BY PORT
# ============================================================

$Ports = @(7010, 7020, 7030, 6969, 11434)

foreach ($Port in $Ports) {

    $connections = Get-NetTCPConnection `
        -LocalPort $Port `
        -State Listen `
        -ErrorAction SilentlyContinue

    foreach ($connection in $connections) {

        $processId = $connection.OwningProcess

        Write-Host "Stopping process $processId on port $Port..."

        Stop-Process `
            -Id $processId `
            -Force `
            -ErrorAction SilentlyContinue
    }
}


# ============================================================
# STOP LEFTOVER PROJECT PYTHON PROCESSES
# ============================================================

$ProjectRoot = "C:\AI\ProjectJarvis"

$projectPythonProcesses = Get-CimInstance Win32_Process `
    -Filter "Name = 'python.exe'" `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.CommandLine -like "*$ProjectRoot*" -or
        $_.ExecutablePath -like "$ProjectRoot\*"
    }

foreach ($process in $projectPythonProcesses) {

    Write-Host "Stopping Project Jarvis Python process $($process.ProcessId)..."

    Stop-Process `
        -Id $process.ProcessId `
        -Force `
        -ErrorAction SilentlyContinue
}


# ============================================================
# STOP APPLIO WINDOWS / PROCESSES
# ============================================================

$applioProcesses = Get-CimInstance Win32_Process `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.CommandLine -like "*ApplioV3.6.2*" -or
        $_.ExecutablePath -like "*ApplioV3.6.2*"
    }

foreach ($process in $applioProcesses) {

    Write-Host "Stopping Applio process $($process.ProcessId)..."

    Stop-Process `
        -Id $process.ProcessId `
        -Force `
        -ErrorAction SilentlyContinue
}


# ============================================================
# STOP OLLAMA
# ============================================================

Get-Process ollama `
    -ErrorAction SilentlyContinue |
    ForEach-Object {

        Write-Host "Stopping Ollama process $($_.Id)..."

        Stop-Process `
            -Id $_.Id `
            -Force `
            -ErrorAction SilentlyContinue
    }


Write-Host ""
Write-Host "Project Jarvis has been fully stopped." -ForegroundColor Green
Write-Host "Memory, STT, TTS, Applio, Ollama, and Jarvis Python processes were closed."