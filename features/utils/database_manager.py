"""Database management utilities for query execution."""

from contextlib import contextmanager
from typing import List, Dict, Any, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from features.utils.log_manager import get_logger
from features.utils.config_manager import ConfigManager


logger = get_logger(__name__)


class DatabaseManager:
    """Manage database connections and query execution."""

    _instance = None

    def __new__(cls):
        """Singleton pattern - return single instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize database manager with configuration."""
        if self._initialized:
            return

        self.config = ConfigManager()
        self.engine = None
        self.session_factory = None
        self._initialize_engine()
        self._initialized = True

    def _initialize_engine(self):
        """Initialize SQLAlchemy engine based on config."""
        try:
            db_type = self.config.get('postgres_type', 'postgresql+psycopg2')
            db_user = self.config.get('postgres_user')
            db_password = self.config.get('postgres_password')
            db_host = self.config.get('postgres_host')
            db_port = self.config.get('postgres_port', 5432)
            db_name = self.config.get('postgres_database')

            # Construct connection string
            connection_string = f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

            # Create engine with connection pooling
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,  # Recycle connections after 1 hour
                echo=False
            )

            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)

            # Test connection
            with self.engine.connect() as conn:
                logger.info(f"Database connection established: {db_host}:{db_port}/{db_name}")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.

        Args:
            query (str): SQL query string
            params (dict, optional): Query parameters

        Returns:
            List[Dict]: Query results as list of dictionaries
        """
        if not self.engine:
            raise RuntimeError("Database engine not initialized")

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                rows = result.fetchall()
                # Convert Row objects to dictionaries
                return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}\nParams: {params}")
            raise

    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.

        Args:
            query (str): SQL query string
            params (dict, optional): Query parameters

        Returns:
            int: Number of affected rows
        """
        if not self.engine:
            raise RuntimeError("Database engine not initialized")

        try:
            with self.engine.begin() as conn:
                result = conn.execute(text(query), params or {})
                affected_rows = result.rowcount
                logger.info(f"Update query executed: {affected_rows} rows affected")
                return affected_rows
        except Exception as e:
            logger.error(f"Update query failed: {e}\nQuery: {query}\nParams: {params}")
            raise

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        Usage:
            with db.transaction() as session:
                session.execute(...)
                # Auto-rollback on exception, auto-commit on success
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
            logger.info("Transaction committed")
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            session.close()

    def close(self):
        """Close database connection pool."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection pool closed")

    def get_connection(self):
        """Get raw database connection."""
        if not self.engine:
            raise RuntimeError("Database engine not initialized")
        return self.engine.connect()

    def health_check(self) -> bool:
        """
        Check database connectivity.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Convenience function for imports
def get_database_manager() -> DatabaseManager:
    """Get or create DatabaseManager singleton."""
    return DatabaseManager()
