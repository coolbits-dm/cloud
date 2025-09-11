# CoolBits.ai Windows MSI Installer Script
# ========================================

import os
import sys
import subprocess
from pathlib import Path

def create_msi_installer():
    """Create MSI installer for Windows"""
    
    # Create installer directory
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Create WiX configuration
    wxs_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="CoolBits.ai" 
           Language="1033" 
           Version="1.0.0" 
           Manufacturer="COOL BITS SRL" 
           UpgradeCode="PUT-GUID-HERE">
    
    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine" 
             Description="CoolBits.ai AI Platform" />
    
    <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
    <MediaTemplate />
    
    <Feature Id="ProductFeature" Title="CoolBits.ai" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
    
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="CoolBitsAI">
          <Component Id="MainExecutable" Guid="PUT-GUID-HERE">
            <File Id="coolbits_main_dashboard.py" 
                  Source="coolbits_main_dashboard.py" 
                  KeyPath="yes" />
            <File Id="coolbits_main_bridge.py" 
                  Source="coolbits_main_bridge.py" />
            <File Id="requirements.txt" 
                  Source="requirements.txt" />
            <File Id="package.json" 
                  Source="package.json" />
            <File Id="Dockerfile" 
                  Source="Dockerfile" />
            <File Id="docker-compose.yml" 
                  Source="docker-compose.yml" />
            
            <!-- Copy scripts directory -->
            <Directory Id="ScriptsDir" Name="scripts">
              <Component Id="ScriptsComponent" Guid="PUT-GUID-HERE">
                <File Id="autostart.ps1" 
                      Source="scripts/autostart.ps1" />
                <File Id="doctor.ps1" 
                      Source="scripts/doctor.ps1" />
                <File Id="startup.ps1" 
                      Source="scripts/startup.ps1" />
                <File Id="release.py" 
                      Source="scripts/release.py" />
                <File Id="docker-entrypoint.sh" 
                      Source="scripts/docker-entrypoint.sh" />
              </Component>
            </Directory>
            
            <!-- Copy logs directory -->
            <Directory Id="LogsDir" Name="logs">
              <Component Id="LogsComponent" Guid="PUT-GUID-HERE">
                <File Id="boot-health.log" 
                      Source="logs/boot-health.log" />
              </Component>
            </Directory>
          </Component>
        </Directory>
      </Directory>
      
      <!-- Start Menu -->
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="CoolBits.ai">
          <Component Id="ApplicationShortcut" Guid="PUT-GUID-HERE">
            <Shortcut Id="ApplicationStartMenuShortcut"
                      Directory="ApplicationProgramsFolder"
                      Name="CoolBits.ai"
                      WorkingDirectory="INSTALLFOLDER"
                      Icon="ApplicationIcon.exe"
                      IconIndex="0"
                      Advertise="yes" />
            <RemoveFolder Id="ApplicationProgramsFolder" On="uninstall" />
            <RegistryValue Root="HKCU" Key="Software\\CoolBits.ai" Name="installed" Type="integer" Value="1" KeyPath="yes" />
          </Component>
        </Directory>
      </Directory>
      
      <!-- Desktop Shortcut -->
      <Directory Id="DesktopFolder" Name="Desktop">
        <Component Id="DesktopShortcut" Guid="PUT-GUID-HERE">
          <Shortcut Id="DesktopShortcut"
                    Directory="DesktopFolder"
                    Name="CoolBits.ai"
                    WorkingDirectory="INSTALLFOLDER"
                    Icon="ApplicationIcon.exe"
                    IconIndex="0"
                    Advertise="yes" />
          <RemoveFolder Id="DesktopFolder" On="uninstall" />
          <RegistryValue Root="HKCU" Key="Software\\CoolBits.ai" Name="desktop" Type="integer" Value="1" KeyPath="yes" />
        </Component>
      </Directory>
    </Directory>
    
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <ComponentRef Id="MainExecutable" />
      <ComponentRef Id="ScriptsComponent" />
      <ComponentRef Id="LogsComponent" />
      <ComponentRef Id="ApplicationShortcut" />
      <ComponentRef Id="DesktopShortcut" />
    </ComponentGroup>
    
    <!-- Custom Actions -->
    <CustomAction Id="InstallPython" 
                  ExeCommand="python -m pip install -r requirements.txt" 
                  Directory="INSTALLFOLDER" 
                  Execute="deferred" 
                  Return="check" />
    
    <CustomAction Id="StartService" 
                  ExeCommand="powershell -ExecutionPolicy Bypass -File scripts/autostart.ps1 -Action start" 
                  Directory="INSTALLFOLDER" 
                  Execute="deferred" 
                  Return="check" />
    
    <InstallExecuteSequence>
      <Custom Action="InstallPython" After="InstallFiles">NOT Installed</Custom>
      <Custom Action="StartService" After="InstallPython">NOT Installed</Custom>
    </InstallExecuteSequence>
    
  </Product>
</Wix>'''
    
    # Write WiX file
    wxs_file = installer_dir / "CoolBitsAI.wxs"
    with open(wxs_file, 'w') as f:
        f.write(wxs_content)
    
    print(f"✅ Created WiX configuration: {wxs_file}")
    
    # Create batch file for building
    build_script = installer_dir / "build.bat"
    with open(build_script, 'w') as f:
        f.write('''@echo off
echo Building CoolBits.ai MSI Installer...

REM Check if WiX is installed
where candle.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: WiX Toolset not found. Please install WiX Toolset v3.11 or later.
    echo Download from: https://wixtoolset.org/releases/
    pause
    exit /b 1
)

REM Compile WiX source
candle.exe CoolBitsAI.wxs -out CoolBitsAI.wixobj

if %errorlevel% neq 0 (
    echo Error: Failed to compile WiX source
    pause
    exit /b 1
)

REM Link WiX object
light.exe CoolBitsAI.wixobj -out CoolBitsAI.msi

if %errorlevel% neq 0 (
    echo Error: Failed to link WiX object
    pause
    exit /b 1
)

echo ✅ MSI installer created: CoolBitsAI.msi
pause
''')
    
    print(f"✅ Created build script: {build_script}")
    print("📝 To build MSI installer:")
    print("1. Install WiX Toolset v3.11+ from https://wixtoolset.org/releases/")
    print("2. Run: cd installer && build.bat")
    print("3. MSI will be created as CoolBitsAI.msi")

if __name__ == "__main__":
    create_msi_installer()
