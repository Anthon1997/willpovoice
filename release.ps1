# Uso: .\release.ps1 1.2.7 "Notas de la version"
param(
    [Parameter(Mandatory=$true)][string]$Version,
    [string]$Notes = "Mejoras y correcciones."
)
$ErrorActionPreference = "Stop"
Write-Host "Lanzando WillpoVoice v$Version" -ForegroundColor Cyan

$places = @(
    @{ path="app/version.py";      pattern='APP_VERSION\s*=\s*"[^"]+"'; replace="APP_VERSION = `"$Version`"" },
    @{ path="ui/modern_window.py"; pattern='setWindowTitle\("WillpoVoice v[^"]+"\)'; replace="setWindowTitle(`"WillpoVoice v$Version`")" },
    @{ path="ui/modern_window.py"; pattern='QLabel\("v[0-9.]+"\)'; replace="QLabel(`"v$Version`")" },
    @{ path="ui/main_window.py";   pattern='setWindowTitle\("WillpoVoice v[^"]+"\)'; replace="setWindowTitle(`"WillpoVoice v$Version`")" },
    @{ path="installer.iss";       pattern='AppVersion=[0-9.]+'; replace="AppVersion=$Version" },
    @{ path="installer.iss";       pattern='OutputBaseFilename=WillpoVoice-Setup-[0-9.]+'; replace="OutputBaseFilename=WillpoVoice-Setup-$Version" }
)
foreach ($p in $places) {
    $full = (Resolve-Path $p.path).Path
    $c = [System.IO.File]::ReadAllText($full)
    $c = [regex]::Replace($c, $p.pattern, $p.replace)
    [System.IO.File]::WriteAllText($full, $c)
    Write-Host "  OK $($p.path)"
}

.\.venv\Scripts\python.exe -m PyInstaller WillpoVoice.spec --noconfirm
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
$setup = "dist\WillpoVoice-Setup-$Version.exe"
if (-not (Test-Path $setup)) { throw "Instalador no generado" }

git add -A
git commit -m "release: v$Version" -m $Notes
git push

$remote = git remote get-url origin
$remote -match "github\.com[:/]([^/]+)/([^/.]+)" | Out-Null
$ghrepo = "$($matches[1])/$($matches[2])"

# Intentar borrar release previo (ignorar errores si no existe)
try {
    gh release delete "v$Version" --cleanup-tag --yes --repo $ghrepo 2>$null
} catch {}

gh release create "v$Version" $setup --repo $ghrepo --title "WillpoVoice v$Version" --notes $Notes
Write-Host "LISTO v$Version publicado." -ForegroundColor Green
