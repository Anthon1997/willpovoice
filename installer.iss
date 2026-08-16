[Setup]
AppName=WillpoVoice
AppVersion=1.2.7
AppPublisher=WillpoTech
DefaultDirName={autopf}\WillpoVoice
DefaultGroupName=WillpoVoice
OutputDir=dist
OutputBaseFilename=WillpoVoice-Setup-1.2.7
SetupIconFile=assets\icons\icon.ico
UninstallDisplayIcon={app}\WillpoVoice.exe
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\WillpoVoice.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\WillpoKeyGen.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "third_party\NaturalVoiceSAPIAdapter\Installer.exe"; DestDir: "{app}\engine"; Flags: ignoreversion
Source: "third_party\NaturalVoiceSAPIAdapter\x64\*"; DestDir: "{app}\engine\x64"; Flags: ignoreversion recursesubdirs
Source: "installer\adapter_config.reg"; DestDir: "{app}\engine"; Flags: ignoreversion

[Icons]
Name: "{group}\WillpoVoice"; Filename: "{app}\WillpoVoice.exe"
Name: "{group}\Generador de Licencias"; Filename: "{app}\WillpoKeyGen.exe"
Name: "{autodesktop}\WillpoVoice"; Filename: "{app}\WillpoVoice.exe"

[Run]
Filename: "regsvr32.exe"; Parameters: "/s ""{app}\engine\x64\NaturalVoiceSAPIAdapter.dll"""; Flags: runhidden waituntilterminated
Filename: "regedit.exe"; Parameters: "/s ""{app}\engine\adapter_config.reg"""; Flags: runhidden waituntilterminated
Filename: "{app}\WillpoVoice.exe"; Description: "Abrir WillpoVoice"; Flags: nowait postinstall

[UninstallRun]
Filename: "regsvr32.exe"; Parameters: "/u /s ""{app}\engine\x64\NaturalVoiceSAPIAdapter.dll"""; Flags: runhidden waituntilterminated

[Code]
procedure CleanRegistry(RootKey: Integer; BasePath: String);
var
  Names: TArrayOfString;
  I: Integer;
  DisplayName: String;
  SubPath: String;
begin
  if RegGetSubkeyNames(RootKey, BasePath, Names) then
  begin
    for I := 0 to GetArrayLength(Names) - 1 do
    begin
      SubPath := BasePath + '\' + Names[I];
      if RegQueryStringValue(RootKey, SubPath, 'DisplayName', DisplayName) then
      begin
        if Pos('NaturalVoiceSAPIAdapter', DisplayName) > 0 then
          RegDeleteKeyIncludingSubkeys(RootKey, SubPath);
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    CleanRegistry(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall');
    CleanRegistry(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall');
    CleanRegistry(HKCU, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall');
  end;
end;