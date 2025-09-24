# ============================================================================
#region Stage 2: System Configuration for Server Build (Local-Exec Version)
# ============================================================================
# Configures Windows security, performance, and baseline system settings
# Runs from Terraform machine and connects to target VM via WinRM

param(
    $ServerName,
    $TargetServer
)

Write-Host "Starting System Configuration for server: $ServerName"

try {
    if (-not $TargetServer) {
        throw "TargetServer parameter not provided."
    }

    Write-Host "Target Server: $TargetServer"
    Write-Host "Connecting to target server via WinRM using integrated authentication..."

    # Execute system configuration on remote server using integrated authentication
    Invoke-Command -ComputerName $TargetServer -UseSSL -SessionOption (New-PSSessionOption -SkipCACheck -SkipCNCheck -SkipRevocationCheck) -ScriptBlock {
        param($ServerName)
        
        function Write-Log {
            param([string]$Message, [string]$Level = "INFO")
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $logEntry = "$timestamp [$Level] $Message"
            Write-Host $logEntry
            
            # Also log to file
            $logDir = "C:\ServerBuildLogs"
            if (-not (Test-Path $logDir)) {
                New-Item -Path $logDir -ItemType Directory -Force | Out-Null
            }
            $logFile = "$logDir\ServerBuild-$(Get-Date -Format 'yyyy-MM-dd').log"
            Add-Content -Path $logFile -Value $logEntry
        }

        function Write-LogSection {
            param([string]$SectionName)
            $separator = "=" * 60
            Write-Log $separator
            Write-Log "  $SectionName"
            Write-Log $separator
        }

        Write-LogSection "System Configuration"
        Write-Log "Configuring Windows baseline system settings"

        # ============================================================================
        #region Network Interface Standardization
        # ============================================================================
        Write-Log "Standardizing network interface naming"
        try {
            $sourceAdapter = Get-NetAdapter -Name 'Ethernet' -ErrorAction SilentlyContinue
            if ($sourceAdapter) {
                $targetExists = Get-NetAdapter -Name 'Ethernet0' -ErrorAction SilentlyContinue
                
                if ($targetExists) {
                    Write-Log "Adapter 'Ethernet0' already exists - skipping rename" -Level "WARNING"
                } else {
                    $renamedAdapter = Rename-NetAdapter -Name 'Ethernet' -NewName 'Ethernet0' -PassThru
                    Write-Log "Successfully renamed network adapter from 'Ethernet' to 'Ethernet0'" -Level "SUCCESS"
                }
            } else {
                Write-Log "No adapter named 'Ethernet' found - checking for existing 'Ethernet0'"
                $ethernet0 = Get-NetAdapter -Name 'Ethernet0' -ErrorAction SilentlyContinue
                if ($ethernet0) {
                    Write-Log "Adapter 'Ethernet0' already exists - configuration correct" -Level "SUCCESS"
                } else {
                    Write-Log "No standard network adapter found - may need manual configuration" -Level "WARNING"
                }
            }
        } catch {
            Write-Log "Failed to rename network adapter: $($_.Exception.Message)" -Level "ERROR"
        }

        # ============================================================================
        #region IPv6 Disabling
        # ============================================================================
        Write-Log "Disabling IPv6 on all network adapters"
        try {
            $ipv6Bindings = Get-NetAdapterBinding -ComponentID ms_tcpip6
            if ($ipv6Bindings) {
                $enabledBindings = $ipv6Bindings | Where-Object { $_.Enabled -eq $true }
                if ($enabledBindings) {
                    $enabledBindings | Disable-NetAdapterBinding -Confirm:$false
                    Write-Log "IPv6 disabled on $($enabledBindings.Count) network adapter(s)" -Level "SUCCESS"
                } else {
                    Write-Log "IPv6 is already disabled on all adapters" -Level "SUCCESS"
                }
            } else {
                Write-Log "No network adapters found with IPv6 binding" -Level "WARNING"
            }
        } catch {
            Write-Log "Failed to disable IPv6: $($_.Exception.Message)" -Level "ERROR"
        }

        # ============================================================================
        #region NetBIOS Disabling
        # ============================================================================
        Write-Log "Disabling NetBIOS over TCP/IP"
        try {
            # Get all network adapter configurations that have NetBIOS options
            $adapterObjects = Get-WMIObject -Class 'Win32_NetworkAdapterConfiguration' | 
                Where-Object { $_.TcpipNetbiosOptions -ne $null }
            
            if ($adapterObjects) {
                $processedCount = 0
                $alreadyDisabledCount = 0
                
                foreach ($adapterObject in $adapterObjects) {
                    if ($adapterObject.TcpipNetbiosOptions -eq 2) {
                        $alreadyDisabledCount++
                        continue
                    }
                    
                    $result = $adapterObject.SetTcpipNetBios(2)
                    if ($result.ReturnValue -eq 0) {
                        $processedCount++
                    } else {
                        Write-Log "Failed to disable NetBIOS on adapter $($adapterObject.Description): Return code $($result.ReturnValue)" -Level "WARNING"
                    }
                }
                
                Write-Log "NetBIOS disabled on $processedCount adapter(s), $alreadyDisabledCount already disabled" -Level "SUCCESS"
            } else {
                Write-Log "No network adapters found with NetBIOS configuration" -Level "WARNING"
            }
            
            # Disable WINS resolution
            try {
                $winsResult = Invoke-WMIMethod -Class Win32_NetworkAdapterConfiguration -Name EnableWINS -ArgumentList @($false,$false)
                if ($winsResult.ReturnValue -eq 0) {
                    Write-Log "WINS resolution disabled successfully" -Level "SUCCESS"
                } else {
                    Write-Log "WINS disable returned code: $($winsResult.ReturnValue)" -Level "WARNING"
                }
            } catch {
                Write-Log "Failed to disable WINS: $($_.Exception.Message)" -Level "WARNING"
            }
            
        } catch {
            Write-Log "Failed to disable NetBIOS: $($_.Exception.Message)" -Level "ERROR"
        }

        # ============================================================================
        #region Security Hardening
        # ============================================================================
        Write-LogSection "Security Hardening"

        # ============================================================================
        #region Performance Optimization
        # ============================================================================
        Write-LogSection "Performance Optimization"

        # ============================================================================
        #region System Baseline Configuration
        # ============================================================================
        Write-LogSection "System Baseline Configuration"

        Write-Log "System Configuration stage completed"

    } -ArgumentList $ServerName

    Write-Host "System Configuration completed successfully"
}
catch {
    Write-Host "System Configuration failed: $_"
    Write-Host "Error details: $($_.Exception.Message)"
    exit 1
}
