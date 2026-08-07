Write-Host "=== 1. Generando recursos graficos ==="
python scripts\create_exe_icon.py
python scripts\create_spectrum.py
python scripts\create_headset_icon.py
python scripts\create_button_icons.py
python scripts\create_fire_icon.py
python scripts\create_dot_icons.py
python scripts\create_wizard_images.py

Write-Host "=== 2. Compilando ejecutable WillpoVoice ==="
pyinstaller --name WillpoVoice --windowed --onefile --clean --icon=assets\icons\icon.ico --add-data "assets\icons;assets\icons" run.py

Write-Host "=== 3. Creando instalador ==="
$iscc = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (Test-Path $iscc) {
    & $iscc installer\NaturalVoiceTTS.iss
} else {
    Write-Host "Inno Setup no encontrado."
}

Write-Host "=== Build completo ==="
Write-Host "Exe:   dist\WillpoVoice.exe"
Write-Host "Setup: installer\output\WillpoVoice-Setup-1.1.0.exe"
