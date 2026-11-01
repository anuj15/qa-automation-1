# Setup Guide for {{PROJECT_NAME}} QA Automation

## Prerequisites

- **Python 3.11 or higher**
- **Git** (for version control)
- **AWS credentials** (for AWS Secrets Manager access)
- **PowerShell** (on Windows) or **Bash** (on Linux/macOS)

## Installation Steps

### 1. Clone the Repository

```powershell
git clone <repository-url>
cd <project-name>
```

### 2. Create Python Virtual Environment

#### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Linux/macOS (Bash)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Playwright browsers
playwright install chromium firefox webkit
```

### 4. Configure AWS Credentials

The framework uses AWS Secrets Manager for credential management.

#### Local Setup

Configure your AWS profile named `automation`:

```bash
aws configure --profile automation
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-2)
```

Or set environment variables:
```powershell
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
$env:AWS_DEFAULT_REGION = "us-east-2"
```

#### CI/CD Setup

GitHub Actions uses OIDC for AWS authentication (no secrets needed in repo).

### 5. Configure Environment Variables

Create a `.env` file in the project root (local development only):

```ini
# Environment selection
ENVIRONMENT=dev

# User type for credentials
USER_TYPE=default

# Browser configuration
BROWSER=chromium
HEADLESS=false

# AWS
AWS_REGION=us-east-2
```

**Note:** Do NOT commit `.env` files to the repository.

### 6. Run First Test

```powershell
# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Run BVT (smoke tests)
pytest -m bvt -v

# Run a specific test
pytest features/tests/authentication/test_sample_auth.py -v
```

## Troubleshooting

### Issue: "AWS Secrets Manager call failed"

**Solution:**
- Verify AWS credentials are configured: `aws sts get-caller-identity --profile automation`
- Check the AWS region in `config.yml` matches your credentials region
- Ensure the AWS IAM user has `secretsmanager:GetSecretValue` permission

### Issue: "Playwright browser not found"

**Solution:**
```powershell
playwright install chromium firefox webkit
```

### Issue: "config.yml not found"

**Solution:**
- Ensure you're running tests from the project root directory
- Verify `config.yml` exists in the root of the repository

## Configuration Reference

See [configuration.md](configuration.md) for detailed configuration options.

## Running Tests

### Local Development

```powershell
# Run BVT suite
pytest -m bvt -n 2

# Run UI tests
pytest -m ui -v

# Run API tests
pytest -m api -v

# Run specific file
pytest features/tests/authentication/test_sample_auth.py -v

# Run with Allure reporting
pytest -m bvt --alluredir=features/reports/allure-results
allure serve features/reports/allure-results
```

### CI/CD Execution

Tests run automatically via GitHub Actions on:
- Pull requests to `main` or `develop` branches
- Scheduled runs
- Manual dispatch

See `.github/workflows/` for workflow configurations.

## Next Steps

1. Read [project_guide.md](project_guide.md) for domain knowledge
2. Review [style_guide.md](style_guide.md) for coding conventions
3. Create your first test following the sample structure
4. Integrate with your CI/CD pipeline

## Support

For issues or questions:
- Check the troubleshooting section above
- Review existing test examples in `features/tests/`
- Consult [CONTRIBUTING.md](../CONTRIBUTING.md)
- Contact the team maintainers
