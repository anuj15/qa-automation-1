# Configuration Guide for {{PROJECT_NAME}} QA Automation

## Overview

The `config.yml` file is the central configuration source for the test automation framework. It controls:
- Environment settings (dev, stage, prod)
- Browser configuration
- Timeouts and waits
- Credential management
- File paths and reporting

## Configuration Hierarchy

Values are resolved in this priority order:

1. **Environment Variables** (highest priority)
2. **Environment-specific config** (`config.yml[environment][key]`)
3. **Global config** (`config.yml[key]`)

### Example

If `config.yml` has:
```yaml
dynamic_wait_time: 30000
dev:
  dynamic_wait_time: 60000
```

And you run with `environment=dev`:
- `dynamic_wait_time` will be `60000` (from `dev` block)

## Global Settings

| Setting | Type | Options | Description |
|---------|------|---------|-------------|
| `headless` | boolean | `true`, `false` | Run browser in headless mode |
| `browser` | string | `chromium`, `firefox`, `webkit` | Browser to use |
| `environment` | string | `dev`, `stage`, `prod` | Active environment |
| `user_type` | string | `default`, `admin`, ... | Credential set to load |
| `scope` | string | `session`, `function` | Fixture scope |
| `dynamic_wait_time` | integer | milliseconds | Max wait for explicit waits |
| `static_wait_time` | integer | seconds | Sleep time for async operations |

### Example Configuration

```yaml
headless: true
browser: chromium
environment: dev
user_type: default
dynamic_wait_time: 30000
static_wait_time: 7
```

## Environment Blocks

Define separate configurations for each environment:

```yaml
dev:
  base_url: https://dev.example.com
  api_base_url: https://api.dev.example.com
  postgres_host: dev-db.example.com
  secrets:
    username: "ProjectName/qa/dev/username"
    password: "ProjectName/qa/dev/password"

stage:
  base_url: https://stage.example.com
  api_base_url: https://api.stage.example.com
  postgres_host: stage-db.example.com
  secrets:
    username: "ProjectName/qa/stage/username"
    password: "ProjectName/qa/stage/password"

prod:
  base_url: https://example.com
  api_base_url: https://api.example.com
  postgres_host: prod-db.example.com
  secrets:
    username: "ProjectName/qa/prod/username"
    password: "ProjectName/qa/prod/password"
```

## Credential Resolution

The framework retrieves credentials from **AWS Secrets Manager** by default.

### Naming Convention

Credentials follow this pattern:
```
{{PROJECT_NAME}}_{ENVIRONMENT}_{USER_TYPE}_{FIELD}
```

**Example:**
```
PROJECTNAME_DEV_DEFAULT_USERNAME
PROJECTNAME_DEV_DEFAULT_PASSWORD
```

### Credential Types

Define credential fields in the `secrets` section of each environment:

```yaml
dev:
  secrets:
    username: "ProjectName/qa/dev/username"
    password: "ProjectName/qa/dev/password"
    api_token: "ProjectName/qa/dev/api_token"
```

### Retrieving Credentials in Code

```python
from features.utils.config_manager import get_config

config = get_config()

# Get credential for current user type
password = config.get_credential("password", user_type="default")

# Or use default user type
username = config.get_credential("username")
```

## File Paths

Configure where test artifacts are stored:

```yaml
results_location: features/results
auth_file_location: auth/auth.json
test_data_location: features/test_data
report_folder_location: features/reports
log_file_location: features/logs/app.log
allure_result_location: features/reports/allure-results
```

## Database Configuration

For database-dependent tests:

```yaml
dev:
  postgres_host: dev-db.example.com
  postgres_port: 5432
  postgres_database: projectname_qa
  postgres_username: $POSTGRES_USERNAME_DEV  # env var substitution
  postgres_password: $POSTGRES_PASSWORD_DEV
```

## AWS Secrets Manager

### Setup

1. Create a secret in AWS Secrets Manager in your region (e.g., `us-east-2`)
2. Store credentials as key-value pairs
3. Update `secrets` section in `config.yml` with secret names

### Local Testing

Ensure your AWS profile is configured:
```bash
aws configure --profile automation
```

### CI/CD Testing

GitHub Actions automatically assumes the correct AWS role via OIDC.

## Environment Variables Override

Override any config setting via environment variables:

```powershell
# Override environment
$env:environment = "stage"

# Override browser
$env:browser = "firefox"

# Override credential
$env:PROJECTNAME_STAGE_DEFAULT_PASSWORD = "new-password"

# Run tests
pytest -m bvt -n 2
```

## YAML Anchors (DRY)

Use YAML anchors to reduce duplication:

```yaml
dev: &dev_defaults
  base_url: https://dev.example.com
  postgres_host: dev-db.example.com
  # ... other shared settings

stage:
  <<: *dev_defaults  # Inherit all dev settings
  base_url: https://stage.example.com  # Override specific values
  postgres_host: stage-db.example.com
```

## Common Configuration Scenarios

### Local Development (Windows)

```yaml
headless: false
browser: chromium
environment: dev
user_type: default
capture_video_and_trace: true
reuse_auth_state: true
```

### CI/CD Pipeline (GitHub Actions)

```yaml
headless: true
browser: chromium
environment: stage
capture_video_and_trace: false
retry_attempts: 3
```

### Cross-Browser Testing

```yaml
# For Chromium
browser: chromium

# For Firefox
browser: firefox

# For WebKit (Safari)
browser: webkit
```

## Validating Configuration

Check that all required keys are present:

```powershell
# Print loaded configuration
python -c "from features.utils.config_manager import get_config; print(get_config().data)"
```

## Troubleshooting

### "config.yml not found"
- Ensure you're running from the project root directory

### "Failed to load AWS Secret"
- Verify AWS credentials: `aws sts get-caller-identity --profile automation`
- Confirm secret exists in AWS Secrets Manager
- Check region matches (`aws_region` setting)

### Environment variable not resolved
- Use environment variables for overrides, not in `config.yml` values
- Check capitalization matches AWS secret naming

## Next Steps

- Review [setup.md](setup.md) for installation
- Read [style_guide.md](style_guide.md) for best practices
- Check [project_guide.md](project_guide.md) for domain knowledge
