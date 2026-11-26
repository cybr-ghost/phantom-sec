[Setup]
AppId={{B1E4F6F2-75CB-4B28-8D47-4D0EBC0E2A11}
AppName=Phantom Sec
AppVersion=0.1.0
AppPublisher=Phantom Sec contributors
DefaultDirName={autopf}\Phantom Sec
DefaultGroupName=Phantom Sec
OutputDir=..
OutputBaseFilename=Phantom-Sec-Setup-x64
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
PrivilegesRequired=lowest
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\Phantom-Sec.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Phantom Sec"; Filename: "{app}\Phantom-Sec.exe"
Name: "{autodesktop}\Phantom Sec"; Filename: "{app}\Phantom-Sec.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\Phantom-Sec.exe"; Description: "Launch Phantom Sec"; Flags: nowait postinstall skipifsilent
