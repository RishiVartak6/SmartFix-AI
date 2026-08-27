; ─────────────────────────────────────────────────────────────────────────────
; SmartFix AI — Inno Setup Installer Script
; Builds: SmartFix_Setup.exe
; Requirements: Inno Setup 6+ (https://jrsoftware.org/isdl.php)
; ─────────────────────────────────────────────────────────────────────────────

#define MyAppName       "SmartFix AI"
#define MyAppVersion    "1.0.0"
#define MyAppPublisher  "SmartFix Team"
#define MyAppURL        "https://github.com/RishiVartak6/SmartFix-AI"
#define MyAppExeName    "SmartFix AI.exe"

[Setup]
AppId                     = {{A7E3F2C1-88D4-4B0A-9C1F-2E7D3B4A5F6E}
AppName                   = {#MyAppName}
AppVersion                = {#MyAppVersion}
AppPublisher              = {#MyAppPublisher}
AppPublisherURL           = {#MyAppURL}
AppSupportURL             = {#MyAppURL}
AppUpdatesURL             = {#MyAppURL}
DefaultDirName            = {autopf}\SmartFix AI
DefaultGroupName          = SmartFix AI
AllowNoIcons              = yes
LicenseFile               =
PrivilegesRequired        = admin
OutputDir                 = {#SourcePath}\dist\installer
OutputBaseFilename        = SmartFix_Setup
SetupIconFile             =
Compression               = lzma2/ultra64
SolidCompression          = yes
WizardStyle               = modern
WizardSmallImageFile      =
DisableWelcomePage        = no
DisableDirPage            = no
DisableReadyPage          = no
ShowLanguageDialog        = no
UninstallDisplayIcon      = {app}\{#MyAppExeName}
UninstallDisplayName      = {#MyAppName}
CloseApplications         = yes
RestartIfNeededByRun      = no
ChangesEnvironment        = yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";     Description: "Create a &Desktop shortcut";           GroupDescription: "Additional shortcuts:"
Name: "startupicon";     Description: "Start SmartFix AI with &Windows";      GroupDescription: "Additional shortcuts:"

[Files]
; ── SmartFix application files ──────────────────────────────────────────────
Source: "{#SourcePath}\smartfix_app.py";          DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\SmartFix AI.exe";          DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\requirements.txt";         DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\monitor\*";                DestDir: "{app}\monitor"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\data\*";                   DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "{#SourcePath}\install_helper.ps1";       DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\data"
Name: "{app}\logs"
Name: "{app}\monitor"

[Icons]
Name: "{group}\{#MyAppName}";            Filename: "{app}\{#MyAppExeName}"; Comment: "SmartFix AI — Windows Error Monitor"
Name: "{group}\Uninstall {#MyAppName}";  Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}";      Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Auto-start with Windows
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "SmartFix AI"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startupicon

[Run]
; Run the PowerShell install helper (downloads Python, packages, Ollama, llama3)
Filename: "powershell.exe"; \
    Parameters: "-NoProfile -ExecutionPolicy Bypass -WindowStyle Normal -File ""{app}\install_helper.ps1"" -InstallDir ""{app}"""; \
    StatusMsg: "Installing dependencies (Python, PyQt6, Ollama)... This may take 5-15 minutes depending on your internet speed."; \
    Flags: runasoriginaluser waituntilterminated; \
    Description: "Install Python, PyQt6, and Ollama AI engine"

; Launch SmartFix AI after installation
Filename: "{app}\{#MyAppExeName}"; \
    Description: "Launch {#MyAppName} now"; \
    Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "powershell.exe"; \
    Parameters: "-NoProfile -ExecutionPolicy Bypass -Command ""Remove-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name 'SmartFix AI' -ErrorAction SilentlyContinue"""; \
    Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\monitor\__pycache__"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\install_log.txt"

[Code]
var
  DownloadPage: TDownloadWizardPage;

function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    DownloadPage.Show;
    try
      // No bundled downloads — install_helper.ps1 handles everything at runtime
    finally
      DownloadPage.Hide;
    end;
  end;
end;
