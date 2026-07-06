#define MyAppName "HyoImage"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "HyoT"
#define MyAppExeName "HyoImage.exe"

[Setup]
AppId={{A3B8F2E1-4C5D-6E7F-8091-A2B3C4D5E6F7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\HyoT\ImageTools
DefaultGroupName={#MyAppName}
OutputBaseFilename=HyoImage-1.0.1-x64-setup
OutputDir=..\dist
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
PrivilegesRequired=lowest
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "launchapp"; Description: "Launch {#MyAppName}"; GroupDescription: "Finish:"; Flags: unchecked

[Files]
Source: "..\dist\HyoImage\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent; Tasks: launchapp

[UninstallDelete]
Type: dirifempty; Name: "{app}"
