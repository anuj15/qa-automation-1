# Database Queries

This folder contains SQL query definitions for database testing and validation.

## Structure

```
queries/
├── README.md                    # This file
├── base_queries.py              # Common query patterns and base classes
├── sample_data.sql              # Sample test data, cleanup, and audit log schema
└── {{project_name}}/
    ├── users_queries.py         # User-related queries
    ├── data_queries.py          # Data entity queries
    └── audit_queries.py         # Audit trail queries
```

## Query Organization

Organize queries by **domain/entity**:
- `users_queries.py` — User management queries
- `data_queries.py` — Business entity queries
- `audit_queries.py` — Audit and logging queries
- `transactions_queries.py` — Transaction-related queries

## Writing Queries

### 1. Basic Query Class

```python
from features.utils.database_manager import DatabaseManager

class UserQueries:
    """User-related database queries"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_user_by_id(self, user_id):
        """Fetch user by ID"""
        query = """
            SELECT id, username, email, status
            FROM users
            WHERE id = :user_id
        """
        return self.db.execute_query(query, {'user_id': user_id})
    
    def get_user_by_email(self, email):
        """Fetch user by email"""
        query = """
            SELECT id, username, email, status
            FROM users
            WHERE email = :email
        """
        return self.db.execute_query(query, {'email': email})
    
    def create_user(self, username, email, password_hash):
        """Create new user"""
        query = """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (:username, :email, :password_hash, NOW())
            RETURNING id, username, email
        """
        return self.db.execute_query(query, {
            'username': username,
            'email': email,
            'password_hash': password_hash
        })
    
    def update_user_status(self, user_id, status):
        """Update user status"""
        query = """
            UPDATE users
            SET status = :status, updated_at = NOW()
            WHERE id = :user_id
            RETURNING id, status, updated_at
        """
        return self.db.execute_query(query, {
            'user_id': user_id,
            'status': status
        })
    
    def delete_user(self, user_id):
        """Delete user (soft delete via status)"""
        query = """
            UPDATE users
            SET status = 'deleted', deleted_at = NOW()
            WHERE id = :user_id
        """
        return self.db.execute_query(query, {'user_id': user_id})
    
    def count_users(self, status=None):
        """Count total users, optionally by status"""
        if status:
            query = """
                SELECT COUNT(*) as count
                FROM users
                WHERE status = :status
            """
            return self.db.execute_query(query, {'status': status})
        else:
            query = "SELECT COUNT(*) as count FROM users"
            return self.db.execute_query(query)
```

### 2. Complex Queries with Joins

```python
def get_user_with_orders(self, user_id):
    """Fetch user with order history"""
    query = """
        SELECT 
            u.id, u.username, u.email,
            COUNT(o.id) as order_count,
            SUM(o.total_amount) as total_spent,
            MAX(o.created_at) as last_order_date
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.id = :user_id
        GROUP BY u.id, u.username, u.email
    """
    return self.db.execute_query(query, {'user_id': user_id})
```

### 3. Parameterized Queries (ALWAYS Use!)

```python
# ✅ GOOD - Prevents SQL injection
query = "SELECT * FROM users WHERE id = :user_id"
self.db.execute_query(query, {'user_id': user_id})

# ❌ BAD - SQL injection vulnerability!
query = f"SELECT * FROM users WHERE id = {user_id}"
self.db.execute_query(query)
```

## Using Queries in Tests

### Step Definition Example

```python
from features.queries.{{project_name}}.users_queries import UserQueries

@when('I create a new user with "{username}" and "{email}"')
def step_create_user(context, username, email):
    queries = UserQueries()
    context.user = queries.create_user(username, email, 'hashed_password')

@then('the user should exist in database')
def step_verify_user_exists(context):
    queries = UserQueries()
    db_user = queries.get_user_by_id(context.user['id'])
    assert db_user is not None
    assert db_user['username'] == context.user['username']
    assert db_user['email'] == context.user['email']
```

### API Test Example

```python
def test_create_user_via_api_persists_to_db():
    """Verify user created via API is in database"""
    # Create user via API
    api_service = UserAPIService()
    response = api_service.create_user('john_doe', 'john@example.com')
    user_id = response['id']
    
    # Verify in database
    queries = UserQueries()
    db_user = queries.get_user_by_id(user_id)
    assert db_user is not None
    assert db_user['username'] == 'john_doe'
    assert db_user['email'] == 'john@example.com'
```

## Best Practices

### ✅ DO

- Use **parameterized queries** (`:param` syntax) to prevent SQL injection
- Organize queries by **domain/entity** (one file per major entity)
- Add **docstrings** to every query method
- **Cache query objects** in test fixtures when possible
- Return **dictionaries** from queries for easy assertion
- Use **transactions** for test cleanup (rollback after test)
- Write **reusable query methods** that can be called from multiple tests
- Include **timestamps** (created_at, updated_at) in SELECT statements

### ❌ DON'T

- Use string formatting for query parameters (`f"WHERE id = {id}"`)
- Mix SQL with business logic
- Hardcode environment-specific values (use config)
- Create large result sets without pagination
- Write **overly complex queries** (split into smaller methods)
- Leave test data in the database (use rollback)
- Use `SELECT *` in production code (specify columns)

## Common Query Patterns

### Pagination

```python
def get_users_paginated(self, page=1, page_size=10):
    """Fetch users with pagination"""
    offset = (page - 1) * page_size
    query = """
        SELECT id, username, email, status
        FROM users
        ORDER BY id
        LIMIT :limit OFFSET :offset
    """
    return self.db.execute_query(query, {
        'limit': page_size,
        'offset': offset
    })
```

### Filtering

```python
def get_users_by_status(self, status, created_after=None):
    """Fetch users with optional date filter"""
    query = "SELECT * FROM users WHERE status = :status"
    params = {'status': status}
    
    if created_after:
        query += " AND created_at >= :created_after"
        params['created_after'] = created_after
    
    return self.db.execute_query(query, params)
```

### Aggregation

```python
def get_user_statistics(self):
    """Get user statistics"""
    query = """
        SELECT 
            COUNT(*) as total_users,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_users,
            COUNT(DISTINCT created_at::date) as signup_days,
            AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_session_duration
        FROM users
    """
    return self.db.execute_query(query)
```

### Window Functions

```python
def get_user_ranking_by_orders(self):
    """Rank users by order count"""
    query = """
        SELECT 
            u.id, u.username,
            COUNT(o.id) as order_count,
            ROW_NUMBER() OVER (ORDER BY COUNT(o.id) DESC) as rank
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id, u.username
        ORDER BY rank
    """
    return self.db.execute_query(query)
```

## Database-Specific Notes

### PostgreSQL

- Use `:named_parameters` (SQLAlchemy style)
- RETURNING clause for INSERT/UPDATE/DELETE
- Array types: `SELECT array_agg(id) FROM users`
- JSON columns: `SELECT data->>'key' FROM users`
- Full-text search: `to_tsvector()`, `@@` operator

### MySQL

- Use `?` or `:named_parameters` depending on driver
- Use `LAST_INSERT_ID()` to get inserted ID
- No RETURNING clause (use alternative methods)
- Group concatenation: `GROUP_CONCAT()`

### SQLite (Local Testing)

- Use `?` placeholders
- Limited JOIN complexity
- No window functions
- Use for local/CI testing only

## Testing Queries in Isolation

Create test fixtures to validate queries before using in tests:

```python
import pytest
from features.queries.{{project_name}}.users_queries import UserQueries

@pytest.fixture
def user_queries():
    return UserQueries()

def test_get_user_by_id(user_queries):
    """Test user fetch query"""
    # Create test user
    user = user_queries.create_user('test_user', 'test@example.com', 'hashed')
    
    # Fetch and verify
    fetched = user_queries.get_user_by_id(user['id'])
    assert fetched['username'] == 'test_user'
    
    # Cleanup
    user_queries.delete_user(user['id'])

def test_count_users(user_queries):
    """Test user count query"""
    initial_count = user_queries.count_users()
    
    # Create user
    user_queries.create_user('count_test', 'count@example.com', 'hashed')
    
    # Verify count increased
    new_count = user_queries.count_users()
    assert new_count > initial_count
```

## Troubleshooting

### Query Returns Empty Result
- Check parameterized values are correct
- Verify table/column names match database schema
- Run query directly in database client to validate SQL

### Parameterization Errors
- Use `:param_name` syntax (SQLAlchemy format)
- Never use f-strings or string concatenation
- Check parameter dictionary has all required keys

### Connection Issues
- Verify AWS RDS credentials in `config.yml`
- Check security group allows connection
- Validate IAM role has database access (if using IAM auth)

### Performance Issues
- Add indexes for frequently queried columns
- Use LIMIT for large result sets
- Check for missing JOIN conditions (Cartesian product)

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Core Tutorial](https://docs.sqlalchemy.org/en/14/core/tutorial.html)
- [SQL Best Practices](https://use-the-index-luke.com/)

---

**Last Updated:** {{DATE}}
