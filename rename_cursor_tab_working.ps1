# Working PowerShell script to rename Cursor tab to "andrei0001"
# Uses a direct approach with proper handle management

Write-Host "=== Cursor Tab Renamer (Working) ===" -ForegroundColor Magenta
Write-Host "Renaming Cursor tab to 'andrei0001'..." -ForegroundColor White

# Add Windows API functions
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
    
    [DllImport("user32.dll")]
    public static extern bool SetWindowText(IntPtr hWnd, string lpString);
    
    [DllImport("user32.dll")]
    public static extern IntPtr GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);
    
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    
    [DllImport("user32.dll")]
    public static extern IntPtr GetWindow(IntPtr hWnd, uint uCmd);
    
    [DllImport("user32.dll")]
    public static extern bool IsWindow(IntPtr hWnd);
    
    public const uint GW_OWNER = 4;
    
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
"@

# Global variable to store the found window
$script:foundWindow = $null

function Find-AndRename-CursorWindow {
    Write-Host "Searching for Cursor main window..." -ForegroundColor Yellow
    
    # Get Cursor processes
    $cursorProcesses = Get-Process | Where-Object { 
        $_.ProcessName -like "*cursor*" -or 
        $_.ProcessName -like "*Cursor*"
    }
    
    if ($cursorProcesses.Count -eq 0) {
        Write-Host "No Cursor processes found." -ForegroundColor Red
        return $false
    }
    
    Write-Host "Found $($cursorProcesses.Count) Cursor process(es)" -ForegroundColor Green
    
    $script:foundWindow = $null
    $newTitle = "andrei0001"
    
    $enumProc = {
        param($hWnd, $lParam)
        
        try {
            # Check if window is valid and visible
            if (-not [Win32]::IsWindow($hWnd) -or -not [Win32]::IsWindowVisible($hWnd)) {
                return $true
            }
            
            # Get process ID for this window
            $processId = 0
            [Win32]::GetWindowThreadProcessId($hWnd, [ref]$processId)
            
            # Check if this window belongs to a Cursor process
            $matchingProcess = $cursorProcesses | Where-Object { $_.Id -eq $processId }
            if ($matchingProcess) {
                # Get window title
                $windowText = New-Object System.Text.StringBuilder 256
                $titleLength = [Win32]::GetWindowText($hWnd, $windowText, 256)
                $title = $windowText.ToString()
                
                # Look for main window (has title)
                if ($titleLength -gt 0) {
                    Write-Host "Found window: '$title' (Process: $($matchingProcess.ProcessName))" -ForegroundColor Cyan
                    
                    # Try to rename immediately
                    Write-Host "Attempting to rename to '$newTitle'..." -ForegroundColor Yellow
                    
                    $result = [Win32]::SetWindowText($hWnd, $newTitle)
                    
                    if ($result) {
                        Write-Host "Successfully renamed Cursor tab to '$newTitle'" -ForegroundColor Green
                        $script:foundWindow = $true
                        return $false  # Stop enumeration
                    } else {
                        $errorCode = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
                        Write-Host "Failed to rename window. Error code: $errorCode" -ForegroundColor Red
                        
                        # Try with a different approach - find by exact title match
                        if ($title -match "Cursor") {
                            Write-Host "Trying alternative approach..." -ForegroundColor Yellow
                            
                            # Use FindWindow with the exact title
                            $foundWindow = [Win32]::FindWindow($null, $title)
                            if ($foundWindow -ne [IntPtr]::Zero) {
                                $result2 = [Win32]::SetWindowText($foundWindow, $newTitle)
                                if ($result2) {
                                    Write-Host "Successfully renamed using FindWindow approach!" -ForegroundColor Green
                                    $script:foundWindow = $true
                                    return $false
                                }
                            }
                        }
                    }
                }
            }
        }
        catch {
            Write-Host "Exception in window enumeration: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        return $true  # Continue enumeration
    }
    
    [Win32]::EnumWindows($enumProc, [IntPtr]::Zero)
    return $script:foundWindow
}

# Main execution
try {
    $success = Find-AndRename-CursorWindow
    
    if (-not $success) {
        Write-Host "`nCould not rename the Cursor window. Possible reasons:" -ForegroundColor Red
        Write-Host "1. Cursor window is protected by security software" -ForegroundColor Yellow
        Write-Host "2. Cursor is running in a sandboxed environment" -ForegroundColor Yellow
        Write-Host "3. The window title is dynamically generated and changes frequently" -ForegroundColor Yellow
        Write-Host "4. Try running PowerShell as Administrator" -ForegroundColor Yellow
        Write-Host "5. Try closing and reopening Cursor" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Script error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nScript completed." -ForegroundColor Magenta
