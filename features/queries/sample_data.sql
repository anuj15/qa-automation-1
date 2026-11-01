"""Sample SQL fixture data for testing."""

# Sample user data
INSERT_SAMPLE_USERS = """
INSERT INTO users (username, email, password_hash, status, created_at)
VALUES
    ('test_user_1', 'test1@example.com', 'hashed_password_1', 'active', NOW()),
    ('test_user_2', 'test2@example.com', 'hashed_password_2', 'active', NOW()),
    ('test_user_3', 'test3@example.com', 'hashed_password_3', 'inactive', NOW())
ON CONFLICT (email) DO NOTHING;
"""

# Sample data records
INSERT_SAMPLE_DATA = """
INSERT INTO data (name, description, status, created_at)
VALUES
    ('Sample Data 1', 'First test data record', 'active', NOW()),
    ('Sample Data 2', 'Second test data record', 'active', NOW()),
    ('Sample Data 3', 'Third test data record', 'inactive', NOW())
ON CONFLICT (name) DO NOTHING;
"""

# Clean up test data
CLEANUP_TEST_DATA = """
-- Delete test users
DELETE FROM users WHERE email LIKE '%@example.com' OR email LIKE '%test%';

-- Delete test data
DELETE FROM data WHERE name LIKE 'Sample%' OR name LIKE 'Test%';
"""

# Create audit log table
CREATE_AUDIT_LOG = """
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    operation VARCHAR(50) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
"""

# Get user audit history
USER_AUDIT_HISTORY = """
SELECT 
    id, table_name, operation, record_id,
    old_values, new_values, user_id, created_at
FROM audit_log
WHERE table_name = 'users' AND record_id = :user_id
ORDER BY created_at DESC
"""
