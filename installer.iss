[Setup]
AppName=WillpoVoice
AppVersion=1.2.1
AppPublisher=WillpoTech
DefaultDirName={autopf}\WillpoVoice
DefaultGroupName=WillpoVoice
OutputDir=dist
OutputBaseFilename=WillpoVoice-Setup-1.2.1
SetupIconFile=assets\icons\icon.ico
UninstallDisplayIcon={app}\WillpoVoice.exe
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\WillpoVoice.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\WillpoKeyGen.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\WillpoVoice"; Filename: "{app}\WillpoVoice.exe"
Name: "{group}\Generador de Licencias"; Filename: "{app}\WillpoKeyGen.exe"
Name: "{autodesktop}\WillpoVoice"; Filename: "{app}\WillpoVoice.exe"

[Run]
Filename: "{app}\WillpoVoice.exe"; Description: "Abrir WillpoVoice"; Flags: nowait postinstall skipifsilent
