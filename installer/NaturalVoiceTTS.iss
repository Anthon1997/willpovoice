#define MyAppName "WillpoVoice"

#define MyAppVersion "1.5.0"

#define MyAppPublisher "WillpoVoice"

#define MyAppExeName "WillpoVoice.exe"



[Setup]

AppId={{B7E2A4D1-5C3F-4E8A-9D2B-6F1E8C4A7B53}

AppName={#MyAppName}

AppVersion={#MyAppVersion}

AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\WillpoVoice

DefaultGroupName={#MyAppName}

DisableProgramGroupPage=yes

OutputDir=output

OutputBaseFilename=WillpoVoice-Setup-{#MyAppVersion}

Compression=lzma2/max

SolidCompression=yes

ArchitecturesAllowed=x64compatible

ArchitecturesInstallIn64BitMode=x64compatible

UninstallDisplayIcon={app}\{#MyAppExeName}

LicenseFile=..\LICENSE



[Languages]

Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

Name: "english"; MessagesFile: "compiler:Default.isl"



[Tasks]

Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones adicionales:"; Flags: unchecked



[Files]

Source: "sapi_adapter\x64\*"; DestDir: "{app}\sapi\x64"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "adapter_config.reg"; DestDir: "{tmp}"; Flags: confirmoverwrite

Source: "..\dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\voices\Alfredo.safetensors"; DestDir: "{app}\voices"; Flags: ignoreversion



[Icons]

Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon



[Run]

Filename: "C:\Windows\Sysnative\regsvr32.exe"; Parameters: "/s ""{app}\sapi\x64\NaturalVoiceSAPIAdapter.dll"""; Flags: runhidden waituntilterminated

Filename: "{win}\regedit.exe"; Parameters: "/s ""{tmp}\adapter_config.reg"""; StatusMsg: "Aplicando configuracion de 321 voces..."; Flags: runhidden waituntilterminated

Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName} ahora"; Flags: nowait postinstall skipifsilent



[UninstallRun]

Filename: "C:\Windows\Sysnative\regsvr32.exe"; Parameters: "/u /s ""{app}\sapi\x64\NaturalVoiceSAPIAdapter.dll"""; Flags: runhidden waituntilterminated

Filename: "{sys}\reg.exe"; Parameters: "delete ""HKCU\SOFTWARE\NaturalVoiceSAPIAdapter"" /f"; Flags: runhidden waituntilterminated



[Messages]

SetupAppTitle=Instalación

SetupWindowTitle=Instalación - %1

UninstallAppTitle=Desinstalación

UninstallAppFullTitle=Desinstalación de %1



WelcomeLabel1=Bienvenido a WillpoVoice 

WelcomeLabel2=Este asistente instalará WillpoVoice en tu equipo.%n%nTe recomendamos cerrar todas las aplicaciones antes de continuar.



LicenseLabel=Información de licencia

LicenseLabel3=Lee atentamente la siguiente información antes de continuar. Debes aceptar los términos de la licencia para poder instalar [name].



SelectDirLabel3=El asistente instalará WillpoVoice en la siguiente carpeta.

SelectDirBrowseLabel=Para continuar, pulsa Siguiente. Si deseas seleccionar una carpeta diferente, pulsa Examinar.



ReadyLabel1=Listo para instalar

ReadyLabel2a=Pulsa Instalar para continuar con la instalación, o pulsa Atrás si quieres revisar o cambiar alguna opción.



FinishedHeadingLabel=Completando el asistente de WillpoVoice

FinishedLabel=El asistente ha terminado de instalar WillpoVoice en tu equipo.%n%nPuedes ejecutar la aplicación desde el menú inicio o desde el acceso directo del escritorio.



ButtonNext=&Siguiente >

ButtonBack=< &Atrás

ButtonInstall=&Instalar

ButtonFinish=&Finalizar

ButtonCancel=Cancelar



SelectTasksLabel2=Selecciona las tareas adicionales que deben realizarse durante la instalación de WillpoVoice y pulsa Siguiente.































