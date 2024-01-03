!include LogicLib.nsh

# Define installer name and application name
OutFile "PikantoInstaller.exe"
Name "Pikanto"

Icon "assets/icons/app_icon.ico"  # Add this line, replace with the path to your icon

# Default installation directory
InstallDir "$PROGRAMFILES\Pikanto"

# Request admin privileges
RequestExecutionLevel admin

# Pages
Page directory
Page instfiles

# Start installation
Section
    SetOutPath $INSTDIR
    File "C:\Users\user\Documents\GitHub\Projects\Pikanto\myapp\build_cx_freeze\pikanto.zip"  # Replace with the path to your executable
    CreateShortCut "$DESKTOP\Pikanto.lnk" "$INSTDIR\Pikanto.exe"  # Create desktop shortcut
    SetShellVarContext all  # Set permissions for all users
    SetOverwrite on  # Overwrite existing files

    # Write uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"  # Create uninstaller
SectionEnd

# Uninstaller
Section "Uninstall"
    Delete $INSTDIR\Pikanto.exe  # Replace with the name of your executable
    RMDir $INSTDIR
    Delete "$DESKTOP\Pikanto.lnk"  # Remove desktop shortcut during uninstallation
SectionEnd
