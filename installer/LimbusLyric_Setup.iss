#define MyAppName "LimbusLyric"
#define MyAppVersion "1.8.9.136"
#define MyAppPublisher "LimbusLyric"
#define MyAppExeName "LimbusLyric.exe"
#define MyOutputBase "LimbusLyric_Setup_1.8.9.136"

[Setup]
AppId={{44D0F2D8-2C7B-4B24-91E6-911CBA2CB4C7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\LimbusLyric
DefaultGroupName=LimbusLyric
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=release
OutputBaseFilename={#MyOutputBase}
SetupIconFile=..\xiaofen.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
ShowLanguageDialog=no
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
ArchitecturesAllowed=x64compatible

[Languages]
; Keep the previous successful Inno workaround: Default.isl always exists.
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[LangOptions]
LanguageName=简体中文
LanguageID=$0804
LanguageCodePage=936

[Messages]
SetupAppTitle=安装
SetupWindowTitle=安装 - %1
UninstallAppTitle=卸载
UninstallAppFullTitle=%1 卸载
InformationTitle=信息
ConfirmTitle=确认
ErrorTitle=错误
ExitSetupTitle=退出安装程序
ExitSetupMessage=安装尚未完成。如果现在退出，将不会安装该程序。%n%n之后可以再次运行安装程序。%n%n现在退出吗？
ButtonBack=< 上一步(&B)
ButtonNext=下一步(&N) >
ButtonInstall=安装(&I)
ButtonOK=确定
ButtonCancel=取消
ButtonYes=是(&Y)
ButtonNo=否(&N)
ButtonFinish=完成(&F)
ButtonBrowse=浏览(&B)...
ButtonWizardBrowse=浏览(&R)...
ClickNext=点击“下一步”继续，或点击“取消”退出安装程序。
WelcomeLabel1=欢迎使用 [name] 安装向导
WelcomeLabel2=即将在您的计算机上安装 [name/ver]。%n%n建议您在继续安装前关闭其他应用程序。
WizardSelectDir=选择安装位置
SelectDirDesc=您想将 [name] 安装在哪里？
SelectDirLabel3=安装程序将把 [name] 安装到下面的文件夹。
SelectDirBrowseLabel=点击“下一步”继续；如需更改位置，请点击“浏览”。
WizardSelectTasks=选择附加任务
SelectTasksDesc=您希望安装程序执行哪些附加任务？
SelectTasksLabel2=请选择需要的附加任务，然后点击“下一步”。
WizardReady=准备安装
ReadyLabel1=安装程序已准备好安装 [name]。
ReadyLabel2a=点击“安装”开始；如需修改设置，请点击“上一步”。
ReadyLabel2b=点击“安装”开始。
ReadyMemoDir=安装位置：
ReadyMemoTasks=附加任务：
WizardPreparing=正在准备安装
PreparingDesc=安装程序正在准备安装 [name]。
CannotContinue=安装程序无法继续。请点击“取消”退出。
WizardInstalling=正在安装
InstallingLabel=正在安装 [name]，请稍候。
FinishedHeadingLabel=[name] 安装完成
FinishedLabelNoIcons=[name] 已安装到您的计算机。
FinishedLabel=[name] 已安装到您的计算机。您可以通过快捷方式启动它。
ClickFinish=点击“完成”退出安装程序。
RunEntryExec=运行 %1
StatusClosingApplications=正在关闭应用程序...
StatusCreateDirs=正在创建目录...
StatusExtractFiles=正在提取文件...
StatusCreateIcons=正在创建快捷方式...
StatusCreateRegistryEntries=正在创建注册表条目...
StatusSavingUninstall=正在保存卸载信息...
StatusRunProgram=正在完成安装...
SetupAborted=安装未完成。%n%n请修正问题后重新运行安装程序。
ErrorExecutingProgram=无法执行文件：%n%1
ConfirmUninstall=确定要完全移除 %1 及其程序文件吗？诊断日志会保留。
UninstallStatusLabel=正在从您的计算机移除 %1，请稍候。
UninstalledAll=%1 已从您的计算机移除。最近的诊断日志仍保留在当前用户的 LimbusLyric 日志目录中。

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："; Flags: checkedonce

[Dirs]
Name: "{localappdata}\LimbusLyric\logs"; Flags: uninsneveruninstall

[Files]
Source: "..\dist\LimbusLyric\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\LimbusLyric"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\LimbusLyric"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{autoprograms}\LimbusLyric\打开诊断日志"; Filename: "explorer.exe"; Parameters: """{localappdata}\LimbusLyric\logs"""

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 LimbusLyric"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Only delete frozen runtime files. Session logs deliberately live outside {app}
; and survive uninstall/update so users can still report the failure that led to uninstall.
Type: filesandordirs; Name: "{app}\_internal"
