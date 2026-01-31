# Codex配置脚本 (Windows)
# 运行方式: powershell -ExecutionPolicy Bypass -File setup-codex.ps1 -BaseUrl https://your-domain.tld -ApiKey YOUR_KEY
# 或通过一行命令: & { $url='https://your-domain.tld'; $key='YOUR_KEY'; iwr -useb $url/setup-codex.ps1 | iex }

param(
    [string]$BaseUrl,
    [string]$ApiKey,
    [switch]$Test,
    [switch]$Show,
    [switch]$Help
)

# 检查一行命令中的预设变量（使用不同的名称避免冲突）
if (-not $BaseUrl -and (Test-Path Variable:url)) { $BaseUrl = $url }
if (-not $ApiKey -and (Test-Path Variable:key)) { $ApiKey = $key }

# 配置
$DefaultBaseUrl = "http://localhost:8080"
$CodexConfigDir = "$env:USERPROFILE\.codex"
$CodexConfigFile = "$CodexConfigDir\config.toml"

# 输出的颜色函数
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO]" -ForegroundColor Blue -NoNewline
    Write-Host " $Message"
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS]" -ForegroundColor Green -NoNewline
    Write-Host " $Message"
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING]" -ForegroundColor Yellow -NoNewline
    Write-Host " $Message"
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR]" -ForegroundColor Red -NoNewline
    Write-Host " $Message"
}

# 检测 Codex 是否已安装
function Test-Codex {
    try {
        $codexVersion = & codex --version 2>$null
        if ($LASTEXITCODE -eq 0 -and $codexVersion) {
            Write-Success "Codex is already installed: $codexVersion"
            return $true
        }
    }
    catch {
        # 尝试使用 bypass 执行策略运行
        try {
            $codexVersion = powershell -ExecutionPolicy Bypass -Command "codex --version" 2>$null
            if ($codexVersion) {
                Write-Success "Codex is already installed: $codexVersion"
                return $true
            }
        }
        catch {
            # Codex 未安装
        }
    }
    return $false
}

# 检测 Node.js 是否已安装
function Test-NodeJS {
    try {
        $nodeVersion = & node --version 2>$null
        if ($LASTEXITCODE -eq 0 -and $nodeVersion) {
            # 检查 Node.js 版本是否满足要求 (>= 18.0.0)
            $versionPattern = 'v?(\d+)\.(\d+)\.(\d+)'
            if ($nodeVersion -match $versionPattern) {
                $major = [int]$Matches[1]
                if ($major -ge 18) {
                    Write-Success "Node.js is installed: $nodeVersion"
                    return $true
                } else {
                    Write-Warning "Node.js version is too old: $nodeVersion (requires >= 18.0.0)"
                    return $false
                }
            }
        }
    }
    catch {
        # Node.js 未安装
    }
    return $false
}

# 安装 Node.js
function Install-NodeJS {
    Write-Info "Node.js is not installed or version is too old. Installing Node.js..."

    # 检查系统架构
    $arch = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }

    # Node.js 下载地址 (LTS 版本)
    $nodeVersion = "20.18.1"  # LTS 版本
    $nodeUrl = "https://nodejs.org/dist/v$nodeVersion/node-v$nodeVersion-$arch.msi"
    $installerPath = "$env:TEMP\node-installer.msi"

    try {
        Write-Info "Downloading Node.js installer from: $nodeUrl"
        Write-Info "This may take a few minutes depending on your internet connection..."

        # 下载 Node.js 安装程序
        $ProgressPreference = 'SilentlyContinue'  # 禁用进度条以提高下载速度
        Invoke-WebRequest -Uri $nodeUrl -OutFile $installerPath -UseBasicParsing
        $ProgressPreference = 'Continue'

        if (Test-Path $installerPath) {
            Write-Info "Installing Node.js silently..."

            # 静默安装 Node.js
            $installArgs = @(
                "/i",
                "`"$installerPath`"",
                "/quiet",
                "/norestart",
                "ADDLOCAL=ALL"
            )

            $process = Start-Process -FilePath "msiexec.exe" -ArgumentList $installArgs -Wait -PassThru

            if ($process.ExitCode -eq 0) {
                Write-Success "Node.js installed successfully!"

                # 刷新环境变量
                $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

                # 清理安装文件
                Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue

                return $true
            } else {
                Write-Error "Node.js installation failed with exit code: $($process.ExitCode)"
                # 清理安装文件
                Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue
                return $false
            }
        } else {
            Write-Error "Failed to download Node.js installer"
            return $false
        }
    }
    catch {
        Write-Error "Failed to install Node.js: $($_.Exception.Message)"
        return $false
    }
}

# 安装 Codex
function Install-Codex {
    Write-Info "Installing Codex CLI..."

    try {
        # 确保 npm 可用
        $npmVersion = & npm --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "npm is not available. Please restart PowerShell after Node.js installation."
            Write-Info "Run this script again after restarting PowerShell."
            return $false
        }

        Write-Info "npm version: $npmVersion"

        # 安装 Codex CLI
        Write-Info "Running: npm install -g @openai/codex"
        & npm install -g @openai/codex 2>&1 | ForEach-Object { Write-Host $_ }

        if ($LASTEXITCODE -eq 0) {
            # 验证安装
            try {
                $codexVersion = & codex --version 2>&1
                $errorOutput = $codexVersion -join " "

                if ($LASTEXITCODE -eq 0 -and $codexVersion -and -not ($errorOutput -like "*因为在此系统上禁止运行脚本*")) {
                    Write-Success "Codex installed successfully: $codexVersion"
                    return $true
                }

                # 如果包含执行策略错误
                if ($errorOutput -like "*因为在此系统上禁止运行脚本*" -or $errorOutput -like "*disabled on this system*") {
                    Write-Warning "Execution policy is blocking Codex. Trying with bypass..."

                    # 使用 bypass 方式运行
                    try {
                        $codexVersion = powershell -ExecutionPolicy Bypass -Command "codex --version" 2>$null
                        if ($codexVersion) {
                            Write-Success "Codex installed successfully: $codexVersion"
                            Write-Info "Note: Execution policy needs to be set for normal usage."
                            return $true
                        }
                    }
                    catch {
                        # 继续
                    }
                }
            }
            catch {
                # 尝试使用 bypass
                try {
                    $codexVersion = powershell -ExecutionPolicy Bypass -Command "codex --version" 2>$null
                    if ($codexVersion) {
                        Write-Success "Codex installed successfully: $codexVersion"
                        return $true
                    }
                }
                catch {
                    # 继续
                }
            }

            Write-Warning "Codex was installed but cannot be verified."
            return $true
        } else {
            Write-Error "Failed to install Codex via npm"
            return $false
        }
    }
    catch {
        Write-Error "Failed to install Codex: $($_.Exception.Message)"
        return $false
    }
}

# 确保 Codex 已安装
function Ensure-Codex {
    Write-Info "Checking Codex installation..."

    # 检测 Codex 是否已安装
    if (Test-Codex) {
        return $true
    }

    Write-Warning "Codex is not installed"

    # 检测 Node.js 是否已安装
    if (-not (Test-NodeJS)) {
        # 尝试安装 Node.js
        if (-not (Install-NodeJS)) {
            Write-Warning "Failed to install Node.js automatically"
            Write-Info "Please install Node.js manually from: https://nodejs.org/"
            return $false
        }
    }

    # 安装 Codex
    if (Install-Codex) {
        return $true
    } else {
        Write-Warning "Failed to install Codex automatically"
        return $false
    }
}

# 显示帮助的函数
function Show-Help {
    Write-Host @"
Codex Configuration Script (Windows)

Usage: powershell -ExecutionPolicy Bypass -File setup-codex.ps1 [OPTIONS]

Options:
  -BaseUrl <URL> Set the base URL (default: $DefaultBaseUrl)
  -ApiKey <KEY>  Set the API key
  -Test          Test API connection only (requires -BaseUrl and -ApiKey)
  -Show          Show current settings and exit
  -Help          Show this help message

Examples:
  .\setup-codex.ps1 -BaseUrl https://your-domain.tld -ApiKey your-api-key-here
  .\setup-codex.ps1 -Test -BaseUrl https://your-domain.tld -ApiKey your-api-key-here
  .\setup-codex.ps1 -Show

Interactive mode (no arguments):
  .\setup-codex.ps1

PowerShell Execution Policy:
  If you get an execution policy error, run:
  powershell -ExecutionPolicy Bypass -File setup-codex.ps1
"@
    return
}

# 备份现有设置的函数
function Backup-Settings {
    if (Test-Path $CodexConfigFile) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = "$CodexConfigFile.backup.$timestamp"
        Copy-Item -Path $CodexConfigFile -Destination $backupFile
        Write-Info "Backed up existing settings to: $backupFile"
    }
}

# 创建设置目录的函数
function New-SettingsDirectory {
    if (-not (Test-Path $CodexConfigDir)) {
        New-Item -ItemType Directory -Path $CodexConfigDir -Force | Out-Null
        Write-Info "Created Codex configuration directory: $CodexConfigDir"
    }
}

# 验证API密钥格式的函数
function Test-ApiKey {
    param([string]$ApiKey)
    
    if ($ApiKey -match '^[A-Za-z0-9_-]+$') {
        return $true
    } else {
        Write-Error "Invalid API key format. API key should contain only alphanumeric characters, hyphens, and underscores."
        return $false
    }
}

# 测试API连接的函数
function Test-ApiConnection {
    param(
        [string]$BaseUrl,
        [string]$ApiKey
    )
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
            "Authorization" = "Bearer $ApiKey"
        }
        
        # 确定正确的端点
        
        $uri = "$BaseUrl/health"
        $balanceField = "status"
    
        $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers -ErrorAction Stop
        
        if ($response.$balanceField -eq "ok") {
            Write-Success "API connection successful! "
        } else {
            Write-Success "API connection successful!"
        }
        return $true
    }
    catch {
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode -eq 401) {
            Write-Error "API key authentication failed. Please check your API key."
        } elseif ($_.Exception.Message -like "*Unable to connect*" -or $_.Exception.Message -like "*could not be resolved*") {
            Write-Error "Cannot connect to API server. Please check the URL and your internet connection."
        } else {
            Write-Error "API test failed: $($_.Exception.Message)"
        }
        return $false
    }
}

# 创建Codex配置的函数
function New-Settings {
    param(
        [string]$BaseUrl,
        [string]$ApiKey
    )

    $config = @"
model_provider = "codex"
model = "gpt-5.2-codex"
model_reasoning_effort = "high"
disable_response_storage = true

[model_providers.codex]
name = "codex"
base_url = "$BaseUrl"
wire_api = "responses"
env_key = "CODEX_API_KEY"
[features]
web_search_request = true
"@

    try {
        Set-Content -Path $CodexConfigFile -Value $config -Encoding UTF8
        Write-Success "Codex configuration written to: $CodexConfigFile"

        # 设置系统环境变量
        Write-Info "Setting environment variables..."

        # 设置用户环境变量（跨会话持久）
        [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $ApiKey, [EnvironmentVariableTarget]::User)
        [Environment]::SetEnvironmentVariable("CODEX_API_KEY", $ApiKey, [EnvironmentVariableTarget]::User)

        # 同时为当前会话设置
        $env:OPENAI_API_KEY = $ApiKey
        $env:CODEX_API_KEY = $ApiKey

        Write-Success "Environment variables OPENAI_API_KEY and CODEX_API_KEY set successfully"

        return $true
    }
    catch {
        Write-Error "Failed to create configuration: $($_.Exception.Message)"
        return $false
    }
}

# 显示当前设置的函数
function Show-Settings {
    if (Test-Path $CodexConfigFile) {
        Write-Host ""
        Write-Info "Current Codex settings:"
        Write-Host "----------------------------------------"
        Get-Content $CodexConfigFile
        Write-Host "----------------------------------------"
    } else {
        Write-Info "No existing Codex configuration found."
    }

    Write-Host ""
    Write-Info "Current environment variables:"
    Write-Host "----------------------------------------"

    $openaiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", [EnvironmentVariableTarget]::User)
    $codexKey = [Environment]::GetEnvironmentVariable("CODEX_API_KEY", [EnvironmentVariableTarget]::User)

    if ($openaiKey) {
        $maskedKey = if ($openaiKey.Length -gt 12) {
            "$($openaiKey.Substring(0, 8))...$($openaiKey.Substring($openaiKey.Length - 4))"
        } else {
            "$($openaiKey.Substring(0, [Math]::Min(4, $openaiKey.Length)))..."
        }
        Write-Info "OPENAI_API_KEY: $maskedKey"
    } else {
        Write-Info "OPENAI_API_KEY: (not set)"
    }

    if ($codexKey) {
        $maskedKey = if ($codexKey.Length -gt 12) {
            "$($codexKey.Substring(0, 8))...$($codexKey.Substring($codexKey.Length - 4))"
        } else {
            "$($codexKey.Substring(0, [Math]::Min(4, $codexKey.Length)))..."
        }
        Write-Info "CODEX_API_KEY: $maskedKey"
    } else {
        Write-Info "CODEX_API_KEY: (not set)"
    }
    Write-Host "----------------------------------------"
}

# 主函数
function Main {
    Write-Info "Codex Configuration Script"
    Write-Host "======================================="
    Write-Host ""

    # 首先尝试安装 Codex（除非只是显示或测试）
    if (-not $Show -and -not $Test) {
        Ensure-Codex | Out-Null
        Write-Host ""
    }
    
    # 处理命令行参数
    if ($Help) {
        Show-Help
    }
    
    if ($Show) {
        Show-Settings
        return
    }
    
    # 如果未提供URL或密钥，进入交互模式
    if (-not $BaseUrl -and -not $ApiKey) {
        Write-Info "Interactive setup mode"
        Write-Host ""
        
        # 获取基础URL
        $inputUrl = Read-Host "Enter Base URL [$DefaultBaseUrl]"
        if ([string]::IsNullOrWhiteSpace($inputUrl)) {
            $BaseUrl = $DefaultBaseUrl
        } else {
            $BaseUrl = $inputUrl
        }
        
        # 获取API密钥
        while ([string]::IsNullOrWhiteSpace($ApiKey)) {
            $ApiKey = Read-Host "Enter your API key"
            if ([string]::IsNullOrWhiteSpace($ApiKey)) {
                Write-Warning "API key is required"
            } elseif (-not (Test-ApiKey $ApiKey)) {
                $ApiKey = ""
            }
        }
    }
    
    # 验证输入
    if ([string]::IsNullOrWhiteSpace($BaseUrl) -or [string]::IsNullOrWhiteSpace($ApiKey)) {
        Write-Error "Both URL and API key are required"
        Write-Info "Use -Help for usage information"
    }

    # 验证API密钥
    if (-not (Test-ApiKey $ApiKey)) {
    }
    
    # 移除URL末尾的斜杠
    $BaseUrl = $BaseUrl.TrimEnd('/')
    
    Write-Info "Configuration:"
    Write-Info "  Base URL: $BaseUrl"
    $maskedKey = if ($ApiKey.Length -gt 12) { 
        "$($ApiKey.Substring(0, 8))...$($ApiKey.Substring($ApiKey.Length - 4))" 
    } else { 
        "$($ApiKey.Substring(0, [Math]::Min(4, $ApiKey.Length)))..." 
    }
    Write-Info "  API Key: $maskedKey"
    Write-Host ""
    
    # 测试API连接
    $connectionSuccess = Test-ApiConnection -BaseUrl $BaseUrl -ApiKey $ApiKey
    
    if (-not $connectionSuccess) {
        if ($Test) {
        }

        $continue = Read-Host "API test failed. Continue anyway? (y/N)"
        if ($continue -notmatch '^[Yy]$') {
            Write-Info "Setup cancelled"
        }
    }
    
    # 如果仅测试则退出
    if ($Test) {
        Write-Success "API test completed successfully"
        return
    }
    
    # 创建设置目录
    New-SettingsDirectory
    
    # 备份现有设置
    Backup-Settings
    
    # 创建新设置
    if (New-Settings -BaseUrl $BaseUrl -ApiKey $ApiKey) {
        Write-Host ""
        Write-Info "Environment variables OPENAI_API_KEY and CODEX_API_KEY have been set"
        Write-Host ""

        # 检查 Codex 是否已安装并给出相应提示
        $codexCmd = Get-Command codex -ErrorAction SilentlyContinue
        if ($codexCmd) {
            Write-Success "Codex is installed and ready to use!"

            # 检查执行策略并尝试设置
            Write-Host ""
            Write-Info "Checking execution policy..."

            $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

            try {
                $currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
                if ($currentPolicy -eq "Restricted" -or $currentPolicy -eq "AllSigned") {
                    if ($isAdmin) {
                        Write-Info "Setting execution policy to RemoteSigned..."
                        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                        Write-Success "Execution policy set successfully!"
                    } else {
                        Write-Warning "Execution policy needs to be changed for Codex to run properly."
                        Write-Host ""
                        Write-Info "请以管理员身份运行以下命令 / Please run as Administrator:"
                        Write-Info "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
                        Write-Host ""
                        Write-Info "或者每次使用时运行 / Or run each time:"
                        Write-Info "  powershell -ExecutionPolicy Bypass -Command 'codex'"
                    }
                } else {
                    Write-Success "Execution policy is already configured properly."
                }
            }
            catch {
                if ($isAdmin) {
                    try {
                        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                        Write-Success "Execution policy set successfully!"
                    }
                    catch {
                        Write-Warning "Failed to set execution policy: $($_.Exception.Message)"
                    }
                } else {
                    Write-Warning "由于Windows系统限制，需要设置执行策略 / Due to Windows restrictions, execution policy needs to be set:"
                    Write-Info "请以管理员身份运行 / Please run as Administrator:"
                    Write-Info "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
                }
            }

            Write-Host ""
            Write-Info "Run 'codex --version' to verify installation"
        } else {
            Write-Warning "Codex not installed. To install manually:"
            Write-Info "1. Install Node.js from https://nodejs.org/"
            Write-Info "2. Run: npm install -g @openai/codex"
        }
        
        if (Test-Path $CodexConfigFile) {
            Write-Host ""
            Write-Info "Current settings:"
            Get-Content $CodexConfigFile
        }
    } else {
        Write-Error "Failed to create Codex settings"
    }
}

# 运行主函数
Main
