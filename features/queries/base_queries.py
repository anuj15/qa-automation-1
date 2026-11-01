"""Base query class with common database operations."""

from features.utils.log_manager import get_logger
from features.utils.config_manager import ConfigManager


logger = get_logger(__name__)


class BaseQueries:
    """Base class for all query modules."""

    def __init__(self):
        """Initialize base queries with database manager."""
        self.config = ConfigManager()
        self.db = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize database connection (lazy load)."""
        try:
            from features.utils.database_manager import DatabaseManager
            self.db = DatabaseManager()
            logger.info("Database connection initialized")
        except ImportError:
            logger.warning("DatabaseManager not available - database tests will be skipped")

    def check_record_exists(self, table, **conditions):
        """
        Check if a record exists in a table.

        Args:
            table (str): Table name
            **conditions: Column=value pairs for WHERE clause

        Returns:
            bool: True if record exists, False otherwise
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        where_clauses = [f"{col} = :{col}" for col in conditions.keys()]
        where_sql = " AND ".join(where_clauses)
        query = f"SELECT 1 FROM {table} WHERE {where_sql} LIMIT 1"

        try:
            result = self.db.execute_query(query, conditions)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error checking record existence: {e}")
            return False

    def get_record_count(self, table, **conditions):
        """
        Count records in a table.

        Args:
            table (str): Table name
            **conditions: Column=value pairs for WHERE clause

        Returns:
            int: Record count
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        query = f"SELECT COUNT(*) as count FROM {table}"
        params = {}

        if conditions:
            where_clauses = [f"{col} = :{col}" for col in conditions.keys()]
            query += " WHERE " + " AND ".join(where_clauses)
            params = conditions

        try:
            result = self.db.execute_query(query, params)
            return result[0]['count'] if result else 0
        except Exception as e:
            logger.error(f"Error counting records: {e}")
            return 0

    def delete_records(self, table, **conditions):
        """
        Delete records from a table.

        Args:
            table (str): Table name
            **conditions: Column=value pairs for WHERE clause

        Returns:
            int: Number of deleted records
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        where_clauses = [f"{col} = :{col}" for col in conditions.keys()]
        where_sql = " AND ".join(where_clauses)
        query = f"DELETE FROM {table} WHERE {where_sql}"

        try:
            result = self.db.execute_update(query, conditions)
            logger.info(f"Deleted {result} records from {table}")
            return result
        except Exception as e:
            logger.error(f"Error deleting records: {e}")
            return 0

    def get_columns(self, table):
        """
        Get all columns for a table.

        Args:
            table (str): Table name

        Returns:
            list: Column names
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        # Works for PostgreSQL
        query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position
        """
        try:
            result = self.db.execute_query(query, {'table_name': table})
            return [row['column_name'] for row in result]
        except Exception as e:
            logger.error(f"Error getting columns: {e}")
            return []

    def table_exists(self, table):
        """
        Check if a table exists in database.

        Args:
            table (str): Table name

        Returns:
            bool: True if table exists
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        # Works for PostgreSQL
        query = """
            SELECT 1 FROM information_schema.tables
            WHERE table_name = :table_name
        """
        try:
            result = self.db.execute_query(query, {'table_name': table})
            return len(result) > 0
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False


# Example: Users Query Module
class UserQueries(BaseQueries):
    """User-related database queries."""

    def get_user_by_id(self, user_id):
        """
        Fetch user by ID.

        Args:
            user_id: User ID

        Returns:
            dict: User record
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        query = """
            SELECT id, username, email, status, created_at, updated_at
            FROM users
            WHERE id = :user_id
        """
        result = self.db.execute_query(query, {'user_id': user_id})
        return result[0] if result else None

    def get_user_by_email(self, email):
        """
        Fetch user by email.

        Args:
            email: User email

        Returns:
            dict: User record
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        query = """
            SELECT id, username, email, status, created_at, updated_at
            FROM users
            WHERE email = :email
        """
        result = self.db.execute_query(query, {'email': email})
        return result[0] if result else None

    def create_user(self, username, email, password_hash):
        """
        Create new user.

        Args:
            username (str): Username
            email (str): Email address
            password_hash (str): Hashed password

        Returns:
            dict: Created user record
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        query = """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (:username, :email, :password_hash, NOW())
            RETURNING id, username, email, status, created_at
        """
        result = self.db.execute_query(query, {
            'username': username,
            'email': email,
            'password_hash': password_hash
        })
        return result[0] if result else None

    def update_user_status(self, user_id, status):
        """
        Update user status.

        Args:
            user_id: User ID
            status (str): New status

        Returns:
            dict: Updated user record
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        query = """
            UPDATE users
            SET status = :status, updated_at = NOW()
            WHERE id = :user_id
            RETURNING id, status, updated_at
        """
        result = self.db.execute_query(query, {
            'user_id': user_id,
            'status': status
        })
        return result[0] if result else None

    def count_active_users(self):
        """
        Count active users.

        Returns:
            int: Number of active users
        """
        return self.get_record_count('users', status='active')

    def delete_user(self, user_id):
        """
        Delete user (soft delete).

        Args:
            user_id: User ID

        Returns:
            bool: Success status
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        query = """
            UPDATE users
            SET status = 'deleted', deleted_at = NOW()
            WHERE id = :user_id
        """
        try:
            self.db.execute_update(query, {'user_id': user_id})
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False


# Example: Data Query Module
class DataQueries(BaseQueries):
    """Business entity data queries."""

    def get_data_by_id(self, data_id):
        """
        Fetch data record by ID.

        Args:
            data_id: Data ID

        Returns:
            dict: Data record
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        query = """
            SELECT id, name, description, status, created_at, updated_at
            FROM data
            WHERE id = :data_id
        """
        result = self.db.execute_query(query, {'data_id': data_id})
        return result[0] if result else None

    def create_data(self, name, description):
        """
        Create new data record.

        Args:
            name (str): Data name
            description (str): Data description

        Returns:
            dict: Created data record
        """
        if not self.db:
            raise RuntimeError("Database not initialized")

        query = """
            INSERT INTO data (name, description, created_at)
            VALUES (:name, :description, NOW())
            RETURNING id, name, description, status, created_at
        """
        result = self.db.execute_query(query, {
            'name': name,
            'description': description
        })
        return result[0] if result else None

    def count_data_by_status(self, status):
        """
        Count data records by status.

        Args:
            status (str): Status value

        Returns:
            int: Record count
        """
        return self.get_record_count('data', status=status)
