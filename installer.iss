[Setup]
AppName=WillpoVoice
AppVersion=1.2.5
AppPublisher=WillpoTech
DefaultDirName={autopf}\WillpoVoice
DefaultGroupName=WillpoVoice
OutputDir=dist
OutputBaseFilename=WillpoVoice-Setup-1.2.5
SetupIconFile=assets\icons\icon.ico
UninstallDisplayIcon={app}\WillpoVoice.exe
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\WillpoVoice.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\WillpoKeyGen.exe"; DestDir: "{app}"; Flags: ignoreversion
; Motor de voces integrado (NaturalVoiceSAPIAdapter) dentro de WillpoVoice
Source: "third_party\NaturalVoiceSAPIAdapter\Installer.exe"; DestDir: "{app}\engine"; Flags: ignoreversion
Source: "third_party\NaturalVoiceSAPIAdapter\x64\*"; DestDir: "{app}\engine\x64"; Flags: ignoreversion recursesubdirs
Source: "installer\adapter_config.reg"; DestDir: "{app}\engine"; Flags: ignoreversion

[Icons]
Name: "{group}\WillpoVoice"; Filename: "{app}\WillpoVoice.exe"
Name: "{group}\Generador de Licencias"; Filename: "{app}\WillpoKeyGen.exe"
Name: "{autodesktop}\WillpoVoice"; Filename: "{app}\WillpoVoice.exe"

[Run]
; Instala el motor de voces en silencio (sin ventanas, sin entrada en Panel de Control)
Filename: "{app}\engine\Installer.exe"; Parameters: "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART"; Flags: runhidden waituntilterminated skipifsilent
; Aplica configuracion de voces (todas las multilingues habilitadas)
Filename: "regedit.exe"; Parameters: "/s ""{app}\engine\adapter_config.reg"""; Flags: runhidden waituntilterminated skipifsilent
Filename: "{app}\WillpoVoice.exe"; Description: "Abrir WillpoVoice"; Flags: nowait postinstall skipifsilent



[UninstallRun]
; Desregistra el motor de voces al desinstalar WillpoVoice
Filename: "regsvr32.exe"; Parameters: "/u /s ""{app}\engine\x64\NaturalVoiceSAPIAdapter.dll"""; Flags: runhidden waituntilterminated
