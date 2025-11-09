# Setup OpenAI Microphone Bridge - CoolBits.ai
# Instalează dependențele pentru conectarea la OpenAI și accesul la microfon

Write-Host "🚀 Setting up OpenAI Microphone Bridge..." -ForegroundColor Green

# Verifică Python
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Installing..." -ForegroundColor Red
    winget install Python.Python.3.12
    Write-Host "✅ Python installed! Please restart PowerShell and run again." -ForegroundColor Green
    exit
}

# Verifică pip
Write-Host "📦 Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found!" -ForegroundColor Red
    exit
}

# Creează virtual environment
Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv_openai") {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv_openai
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activează virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv_openai\Scripts\Activate.ps1"

# Instalează dependențele
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow

$packages = @(
    "openai",
    "pyaudio",
    "wave",
    "requests"
)

foreach ($package in $packages) {
    Write-Host "📦 Installing $package..." -ForegroundColor Cyan
    try {
        pip install $package
        Write-Host "✅ $package installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install $package" -ForegroundColor Red
    }
}

# Verifică microfonul
Write-Host "🎤 Checking microphone..." -ForegroundColor Yellow
$microphoneDevices = Get-WmiObject -Class Win32_PnPEntity | Where-Object {$_.Name -like "*microphone*" -or $_.Name -like "*mic*"}
if ($microphoneDevices) {
    Write-Host "✅ Microphone devices found:" -ForegroundColor Green
    foreach ($device in $microphoneDevices) {
        Write-Host "  🎤 $($device.Name)" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠️ No microphone devices found" -ForegroundColor Yellow
}

# Verifică OpenAI API Key
Write-Host "🔑 Checking OpenAI API Key..." -ForegroundColor Yellow
$openaiKey = $env:OPENAI_API_KEY
if ($openaiKey) {
    Write-Host "✅ OpenAI API Key found" -ForegroundColor Green
} else {
    Write-Host "❌ OpenAI API Key not found!" -ForegroundColor Red
    Write-Host "💡 Set OPENAI_API_KEY environment variable:" -ForegroundColor Yellow
    Write-Host "   `$env:OPENAI_API_KEY = 'your-api-key-here'" -ForegroundColor Cyan
}

# Creează script de test
Write-Host "🧪 Creating test script..." -ForegroundColor Yellow
$testScript = @"
#!/usr/bin/env python3
import pyaudio
import openai
import os

print("🎤 Testing microphone...")
try:
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print(f"✅ Audio devices: {device_count}")
    
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"🎤 {device_info['name']}")
    
    p.terminate()
    print("✅ Microphone test successful!")
except Exception as e:
    print(f"❌ Microphone test failed: {e}")

print("\n🤖 Testing OpenAI...")
try:
    if os.getenv('OPENAI_API_KEY'):
        client = openai.OpenAI()
        models = client.models.list()
        print(f"✅ OpenAI connected! Models: {len(models.data)}")
    else:
        print("❌ OpenAI API Key not set")
except Exception as e:
    print(f"❌ OpenAI test failed: {e}")
"@

$testScript | Out-File -FilePath "test_openai_microphone.py" -Encoding UTF8
Write-Host "✅ Test script created: test_openai_microphone.py" -ForegroundColor Green

# Creează script de pornire
Write-Host "🚀 Creating startup script..." -ForegroundColor Yellow
$startupScript = @"
# Start OpenAI Microphone Bridge
Write-Host "🎤 Starting OpenAI Microphone Bridge..." -ForegroundColor Green

# Activează virtual environment
& ".\venv_openai\Scripts\Activate.ps1"

# Rulează aplicația
python openai_microphone_bridge.py
"@

$startupScript | Out-File -FilePath "start_openai_microphone.ps1" -Encoding UTF8
Write-Host "✅ Startup script created: start_openai_microphone.ps1" -ForegroundColor Green

Write-Host "`n🎉 OpenAI Microphone Bridge setup completed!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Set OpenAI API Key: `$env:OPENAI_API_KEY = 'your-key'" -ForegroundColor Cyan
Write-Host "2. Test setup: python test_openai_microphone.py" -ForegroundColor Cyan
Write-Host "3. Start bridge: .\start_openai_microphone.ps1" -ForegroundColor Cyan
Write-Host "4. Or run directly: python openai_microphone_bridge.py" -ForegroundColor Cyan

Write-Host "`n🎤 Microphone Bridge Features:" -ForegroundColor Yellow
Write-Host "  - Real-time audio recording" -ForegroundColor Cyan
Write-Host "  - OpenAI Whisper transcription" -ForegroundColor Cyan
Write-Host "  - GPT-4 response generation" -ForegroundColor Cyan
Write-Host "  - Romanian language support" -ForegroundColor Cyan
Write-Host "  - Voice-to-text-to-voice pipeline" -ForegroundColor Cyan
