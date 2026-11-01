# Windows PowerShell script to install dependencies and set up the environment
# Run: .\scripts\install.ps1

# Enable strict error handling
$ErrorActionPreference = "Stop"

Write-Host "======================================"
Write-Host "{{PROJECT_NAME}} QA Automation Setup"
Write-Host "======================================"
Write-Host ""

# Check Python installation
Write-Host "✓ Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion"
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+ and add it to PATH."
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "✓ Creating virtual environment..."
if (Test-Path ".venv") {
    Write-Host "  Virtual environment already exists."
} else {
    python -m venv .venv
    Write-Host "  Virtual environment created at .venv/"
}

# Activate virtual environment
Write-Host ""
Write-Host "✓ Activating virtual environment..."
& ".\.venv\Scripts\Activate.ps1"
Write-Host "  Virtual environment activated."

# Upgrade pip
Write-Host ""
Write-Host "✓ Upgrading pip..."
python -m pip install --upgrade pip
Write-Host "  pip upgraded."

# Install dependencies
Write-Host ""
Write-Host "✓ Installing project dependencies..."
pip install -r requirements.txt
Write-Host "  Requirements installed."

# Install development dependencies
Write-Host ""
Write-Host "✓ Installing development dependencies..."
pip install -r requirements-dev.txt
Write-Host "  Dev requirements installed."

# Install Playwright browsers
Write-Host ""
Write-Host "✓ Installing Playwright browsers..."
playwright install chromium firefox webkit
Write-Host "  Browsers installed."

# Check AWS credentials
Write-Host ""
Write-Host "✓ Checking AWS credentials..."
try {
    $awsIdentity = aws sts get-caller-identity --profile automation 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  AWS profile 'automation' found and valid."
    } else {
        Write-Host "  ⚠ AWS profile 'automation' not configured."
        Write-Host "  Run: aws configure --profile automation"
    }
} catch {
    Write-Host "  ⚠ AWS CLI not found or not configured."
    Write-Host "  To use AWS Secrets Manager, install AWS CLI and configure credentials."
}

Write-Host ""
Write-Host "======================================"
Write-Host "✓ Setup Complete!"
Write-Host "======================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review config.yml and update with your settings"
Write-Host "2. Set environment variables in .env (local development only)"
Write-Host "3. Configure AWS credentials: aws configure --profile automation"
Write-Host "4. Run first test: pytest -m bvt -v"
Write-Host ""
Write-Host "For detailed setup instructions, see: docs/setup.md"
Write-Host ""
