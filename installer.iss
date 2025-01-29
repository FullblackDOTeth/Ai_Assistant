#define MyAppName "Head AI"
#define MyAppVersion "1.0"
#define MyAppPublisher "FullblackDOTeth"
#define MyAppExeName "run_assistant.bat"

[Setup]
AppId={{A7E3B894-9D5F-45E8-8E3D-F2F7E5B3F299}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=HeadAI_Setup
Compression=lzma
SolidCompression=yes
DisableDirPage=no
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Include Python embedded distribution
Source: "python-3.8.10-embed-amd64\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs
; Include your application files
Source: "src\*"; DestDir: "{app}\src"; Flags: ignoreversion recursesubdirs
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "setup.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "run_assistant.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.example"; DestDir: "{app}"; DestName: ".env"; Flags: ignoreversion
Source: "scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion recursesubdirs
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs

[Dirs]
Name: "{app}\logs"
Name: "{app}\data"
Name: "{app}\conversations"
Name: "{app}\venv"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Documentation"; Filename: "{app}\docs\TESTING.md"

[Run]
; Run setup after installation
Filename: "{app}\setup.bat"; Description: "Run initial setup"; Flags: postinstall runhidden
; Show readme after installation
Filename: "{app}\docs\TESTING.md"; Description: "View documentation"; Flags: postinstall shellexec

[UninstallDelete]
Type: filesandordirs; Name: "{app}\venv"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\data"
Type: filesandordirs; Name: "{app}\conversations"
