# scripts/start_jarvis.ps1

$ErrorActionPreference = "Stop"

# ============================================================
# PATHS
# ============================================================

$ProjectRoot = "C:\AI\ProjectJarvis"
$ApplioRoot = "C:\AI\Tools\ApplioV3.6.2"

$MemoryPython = Join-Path $ProjectRoot "memory_venv\Scripts\python.exe"
$SttPython    = Join-Path $ProjectRoot "stt_venv\Scripts\python.exe"
$TtsPython    = Join-Path $ProjectRoot "tts_venv\Scripts\python.exe"
$AgentPython  = Join-Path $ProjectRoot "agent_venv\Scripts\python.exe"

$MemoryServer = Join-Path $ProjectRoot "bigbrain\memory_server.py"
$SttServer    = Join-Path $ProjectRoot "bigbrain\stt_server.py"
$TtsServer    = Join-Path $ProjectRoot "bigbrain\tts_server.py"
$VoiceMain    = Join-Path $ProjectRoot "bigbrain\voice_main.py"

$ApplioLauncher = Join-Path $ApplioRoot "run-applio.bat"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

function Test-TcpPort {
    param(
        [string]$HostName,
        [int]$Port
    )

    $client = New-Object System.Net.Sockets.TcpClient

    try {
        $result = $client.BeginConnect($HostName, $Port, $null, $null)
        $connected = $result.AsyncWaitHandle.WaitOne(500)

        if (-not $connected) {
            return $false
        }

        $client.EndConnect($result)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}


function Wait-ForPort {
    param(
        [string]$Name,
        [string]$HostName = "127.0.0.1",
        [int]$Port,
        [int]$TimeoutSeconds = 180
    )

    Write-Host "Waiting for $Name on port $Port..." -ForegroundColor Yellow

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    while ($stopwatch.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        if (Test-TcpPort -HostName $HostName -Port $Port) {
            Write-Host "$Name is online." -ForegroundColor Green
            return
        }

        Start-Sleep -Seconds 1
    }

    throw "$Name did not start within $TimeoutSeconds seconds."
}


function Confirm-FileExists {
    param(
        [string]$Path,
        [string]$Description
    )

    if (-not (Test-Path $Path)) {
        throw "$Description was not found:`n$Path"
    }
}


function Start-PythonWindow {
    param(
        [string]$Title,
        [string]$PythonPath,
        [string]$ScriptPath
    )

    $command = @"
`$Host.UI.RawUI.WindowTitle = '$Title'
Set-Location '$ProjectRoot'
& '$PythonPath' '$ScriptPath'
"@

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", $command
    )
}


# ============================================================
# VALIDATE FILES
# ============================================================

Write-Host ""
Write-Host "Validating Project Jarvis files..." -ForegroundColor Cyan

Confirm-FileExists $ApplioLauncher "Applio launcher"

Confirm-FileExists $MemoryPython "Memory venv Python"
Confirm-FileExists $SttPython "STT venv Python"
Confirm-FileExists $TtsPython "TTS venv Python"
Confirm-FileExists $AgentPython "Agent venv Python"

Confirm-FileExists $MemoryServer "Memory server"
Confirm-FileExists $SttServer "STT server"
Confirm-FileExists $TtsServer "TTS server"
Confirm-FileExists $VoiceMain "Voice main"

Write-Host "All required files were found." -ForegroundColor Green


# ============================================================
# START OLLAMA IF NEEDED
# ============================================================

if (-not (Test-TcpPort -HostName "127.0.0.1" -Port 11434)) {
    Write-Host ""
    Write-Host "Ollama is not running. Starting Ollama..." -ForegroundColor Cyan

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-Command",
        "`$Host.UI.RawUI.WindowTitle = 'Jarvis - Ollama'; ollama serve"
    )

    Wait-ForPort -Name "Ollama" -Port 11434 -TimeoutSeconds 60
}
else {
    Write-Host "Ollama is already running." -ForegroundColor Green
}


# ============================================================
# START APPLIO
# ============================================================

if (-not (Test-TcpPort -HostName "127.0.0.1" -Port 6969)) {
    Write-Host ""
    Write-Host "Starting Applio..." -ForegroundColor Cyan

    Start-Process cmd.exe `
        -WorkingDirectory $ApplioRoot `
        -ArgumentList "/k", "`"$ApplioLauncher`""

    Wait-ForPort -Name "Applio" -Port 6969 -TimeoutSeconds 180
}
else {
    Write-Host "Applio is already running." -ForegroundColor Green
}


# ============================================================
# START MEMORY SERVER
# ============================================================

if (-not (Test-TcpPort -HostName "127.0.0.1" -Port 7010)) {
    Write-Host ""
    Write-Host "Starting memory server..." -ForegroundColor Cyan

    Start-PythonWindow `
        -Title "Jarvis - Memory Server" `
        -PythonPath $MemoryPython `
        -ScriptPath $MemoryServer

    Wait-ForPort -Name "Memory server" -Port 7010 -TimeoutSeconds 120
}
else {
    Write-Host "Memory server is already running." -ForegroundColor Green
}


# ============================================================
# START STT SERVER
# ============================================================

if (-not (Test-TcpPort -HostName "127.0.0.1" -Port 7020)) {
    Write-Host ""
    Write-Host "Starting STT server..." -ForegroundColor Cyan

    Start-PythonWindow `
        -Title "Jarvis - STT Server" `
        -PythonPath $SttPython `
        -ScriptPath $SttServer

    Wait-ForPort -Name "STT server" -Port 7020 -TimeoutSeconds 180
}
else {
    Write-Host "STT server is already running." -ForegroundColor Green
}


# ============================================================
# START TTS SERVER
# ============================================================

if (-not (Test-TcpPort -HostName "127.0.0.1" -Port 7030)) {
    Write-Host ""
    Write-Host "Starting TTS server..." -ForegroundColor Cyan

    Start-PythonWindow `
        -Title "Jarvis - TTS Server" `
        -PythonPath $TtsPython `
        -ScriptPath $TtsServer

    Wait-ForPort -Name "TTS server" -Port 7030 -TimeoutSeconds 240
}
else {
    Write-Host "TTS server is already running." -ForegroundColor Green
}


# ============================================================
# START JARVIS VOICE MODE
# ============================================================

Write-Host ""
Write-Host "All Jarvis services are online." -ForegroundColor Green
Write-Host "Starting Jarvis voice mode..." -ForegroundColor Cyan
Write-Host ""

Set-Location $ProjectRoot

& $AgentPython $VoiceMain