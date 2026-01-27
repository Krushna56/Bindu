"""OAuth provider configurations - supports unlimited dynamic providers.

Providers are configured via environment variables:
    OAUTH_PROVIDERS__<PROVIDER>__NAME=Display Name
    OAUTH_PROVIDERS__<PROVIDER>__AUTH_URL=https://...
    OAUTH_PROVIDERS__<PROVIDER>__TOKEN_URL=https://...
    OAUTH_PROVIDERS__<PROVIDER>__CLIENT_ID=...
    OAUTH_PROVIDERS__<PROVIDER>__CLIENT_SECRET=...
    OAUTH_PROVIDERS__<PROVIDER>__SCOPE=scope1 scope2

Example:
    OAUTH_PROVIDERS__NOTION__NAME=Notion
    OAUTH_PROVIDERS__NOTION__AUTH_URL=https://api.notion.com/v1/oauth/authorize
    OAUTH_PROVIDERS__NOTION__TOKEN_URL=https://api.notion.com/v1/oauth/token
    OAUTH_PROVIDERS__NOTION__CLIENT_ID=your-client-id
    OAUTH_PROVIDERS__NOTION__CLIENT_SECRET=your-client-secret
    OAUTH_PROVIDERS__NOTION__SCOPE=
"""

from __future__ import annotations

import os
from typing import Optional

from bindu.utils.logging import get_logger

logger = get_logger("bindu.auth.oauth.providers")


def _load_providers_from_env() -> dict:
    """Load OAuth provider configurations from environment variables.
    
    Scans environment for OAUTH_PROVIDERS__<PROVIDER>__* variables
    and builds provider configuration dictionary.
    
    Returns:
        Dictionary of provider configurations
    """
    providers = {}
    
    # Scan environment for provider configs
    for key, value in os.environ.items():
        if not key.startswith("OAUTH_PROVIDERS__"):
            continue
        
        # Parse: OAUTH_PROVIDERS__NOTION__AUTH_URL
        parts = key.split("__")
        if len(parts) != 3:
            continue
        
        provider_name = parts[1].lower()
        config_key = parts[2].lower()
        
        # Initialize provider dict if needed
        if provider_name not in providers:
            providers[provider_name] = {
                "response_type": "code",  # Default
            }
        
        # Map config keys
        if config_key == "name":
            providers[provider_name]["name"] = value
        elif config_key == "auth_url":
            providers[provider_name]["auth_url"] = value
        elif config_key == "token_url":
            providers[provider_name]["token_url"] = value
        elif config_key == "client_id":
            providers[provider_name]["client_id"] = value
        elif config_key == "client_secret":
            providers[provider_name]["client_secret"] = value
        elif config_key == "scope":
            providers[provider_name]["scope"] = value
        elif config_key == "response_type":
            providers[provider_name]["response_type"] = value
    
    return providers


# Load providers from environment at module import
OAUTH_PROVIDERS = _load_providers_from_env()


def get_provider_config(provider: str) -> Optional[dict]:
    """Get OAuth provider configuration.

    Args:
        provider: Provider name (e.g., notion, gmail, slack, dropbox, etc.)

    Returns:
        Provider config dict with all necessary fields, or None if not configured

    Example:
        config = get_provider_config("notion")
        if config:
            client_id = config["client_id"]
            auth_url = config["auth_url"]
    """
    if provider not in OAUTH_PROVIDERS:
        logger.debug(f"Provider '{provider}' not configured")
        return None

    config = OAUTH_PROVIDERS[provider]
    
    # Validate required fields
    required_fields = ["auth_url", "token_url", "client_id", "client_secret"]
    for field in required_fields:
        if not config.get(field):
            logger.warning(f"Provider '{provider}' missing required field: {field}")
            return None
    
    return config.copy()


def list_configured_providers() -> list[str]:
    """List all configured OAuth providers.
    
    Returns:
        List of provider names that are fully configured
        
    Example:
        providers = list_configured_providers()
        # ["notion", "gmail", "slack", "dropbox"]
    """
    configured = []
    for provider in OAUTH_PROVIDERS.keys():
        if get_provider_config(provider) is not None:
            configured.append(provider)
    return configured


def is_provider_configured(provider: str) -> bool:
    """Check if OAuth provider is configured with all required fields.

    Args:
        provider: Provider name

    Returns:
        True if provider has all required fields configured
    """
    config = get_provider_config(provider)
    return config is not None
