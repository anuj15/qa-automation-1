#!/bin/bash
# Linux/macOS shell script to install dependencies and set up the environment
# Run: bash scripts/install.sh

set -e

echo "======================================"
echo "{{PROJECT_NAME}} QA Automation Setup"
echo "======================================"
echo ""

# Check Python installation
echo "✓ Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.11+ and try again."
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "  Found: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "  Virtual environment already exists."
else
    python3 -m venv .venv
    echo "  Virtual environment created at .venv/"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source .venv/bin/activate
echo "  Virtual environment activated."

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
python -m pip install --upgrade pip
echo "  pip upgraded."

# Install dependencies
echo ""
echo "✓ Installing project dependencies..."
pip install -r requirements.txt
echo "  Requirements installed."

# Install development dependencies
echo ""
echo "✓ Installing development dependencies..."
pip install -r requirements-dev.txt
echo "  Dev requirements installed."

# Install Playwright browsers
echo ""
echo "✓ Installing Playwright browsers..."
playwright install chromium firefox webkit
echo "  Browsers installed."

# Check AWS credentials
echo ""
echo "✓ Checking AWS credentials..."
if command -v aws &> /dev/null; then
    if aws sts get-caller-identity --profile automation &> /dev/null; then
        echo "  AWS profile 'automation' found and valid."
    else
        echo "  ⚠ AWS profile 'automation' not configured."
        echo "  Run: aws configure --profile automation"
    fi
else
    echo "  ⚠ AWS CLI not found or not configured."
    echo "  To use AWS Secrets Manager, install AWS CLI and configure credentials."
fi

echo ""
echo "======================================"
echo "✓ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Review config.yml and update with your settings"
echo "2. Set environment variables in .env (local development only)"
echo "3. Configure AWS credentials: aws configure --profile automation"
echo "4. Run first test: pytest -m bvt -v"
echo ""
echo "For detailed setup instructions, see: docs/setup.md"
echo ""
