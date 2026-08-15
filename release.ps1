# Uso: .\release.ps1 1.2.2 "Notas de la version"
param(
    [Parameter(Mandatory=$true)][string]$Version,
    [string]$Notes = "Mejoras y correcciones."
)
$ErrorActionPreference = "Stop"
Write-Host " Lanzando WillpoVoice v$Version" -ForegroundColor Cyan

# 1) Bump de version (6 lugares)
$places = @(
    @{ path="app/version.py";      pattern='APP_VERSION\s*=\s*"[^"]+"'; replace="APP_VERSION = `"$Version`"" },
    @{ path="ui/modern_window.py"; pattern='setWindowTitle\("WillpoVoice v[^"]+"\)'; replace="setWindowTitle(`"WillpoVoice v$Version`")" },
    @{ path="ui/modern_window.py"; pattern='QLabel\("v[0-9.]+"\)'; replace="QLabel(`"v$Version`")" },
    @{ path="ui/main_window.py";   pattern='setWindowTitle\("WillpoVoice v[^"]+"\)'; replace="setWindowTitle(`"WillpoVoice v$Version`")" },
    @{ path="installer.iss";       pattern='AppVersion=[0-9.]+'; replace="AppVersion=$Version" },
    @{ path="installer.iss";       pattern='OutputBaseFilename=WillpoVoice-Setup-[0-9.]+'; replace="OutputBaseFilename=WillpoVoice-Setup-$Version" }
)
foreach ($p in $places) {
    if (Test-Path $p.path) {
        $c = Get-Content $p.path -Raw
        $c = [regex]::Replace($c, $p.pattern, $p.replace)
        Set-Content $p.path -Value $c -Encoding UTF8 -NoNewline
        Write-Host "  OK $($p.path)"
    }
}

# 2) Build EXE + instalador
Write-Host "PyInstaller..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m PyInstaller WillpoVoice.spec --noconfirm
Write-Host "Inno Setup..." -ForegroundColor Yellow
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

$setup = "dist\WillpoVoice-Setup-$Version.exe"
if (-not (Test-Path $setup)) { throw "Instalador no generado" }

# 3) Commit + push del bump
git add -A
git commit -m "release: v$Version" -m $Notes
git push

# 4) GitHub Release con instalador como asset
$remote = git remote get-url origin
$remote -match "github\.com[:/]([^/]+)/([^/.]+)" | Out-Null
$ghrepo = "$($matches[1])/$($matches[2])"
Write-Host "Creando release en $ghrepo..." -ForegroundColor Green
gh release create "v$Version" $setup --repo $ghrepo --title "WillpoVoice v$Version" --notes $Notes
Write-Host "LISTO: los usuarios veran la ventana de actualizacion." -ForegroundColor Green
