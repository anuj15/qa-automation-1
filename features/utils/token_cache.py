"""Token caching for API authentication."""

from typing import Optional


class TokenCache:
    """In-process cache for bearer tokens keyed by user type."""

    def __init__(self) -> None:
        """Initialize the token cache."""
        self._tokens: dict[str, str] = {}

    def set_token(self, token: str, user_type: str = "default") -> None:
        """
        Cache a bearer token for a specific user type.

        :param token: Bearer token string
        :param user_type: User type identifier
        """
        self._tokens[user_type] = token

    def get_token(self, user_type: str = "default") -> Optional[str]:
        """
        Retrieve a cached bearer token for a specific user type.

        :param user_type: User type identifier
        :return: Bearer token or None if not cached
        """
        return self._tokens.get(user_type)

    def clear(self) -> None:
        """Clear all cached tokens."""
        self._tokens.clear()

    def has_token(self, user_type: str = "default") -> bool:
        """Check if a token is cached for the given user type."""
        return user_type in self._tokens


# Global singleton instance
_token_cache = TokenCache()


def get_token_cache() -> TokenCache:
    """Return the global token cache instance."""
    return _token_cache
