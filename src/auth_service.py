"""
API Key Authentication Service
"""
import hashlib
import secrets
import json
import os
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.api_keys_file = "api_keys.json"
        self.api_keys = self._load_api_keys()
    
    def _load_api_keys(self) -> Dict[str, Dict]:
        """Load API keys from file."""
        if os.path.exists(self.api_keys_file):
            try:
                with open(self.api_keys_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading API keys: {e}")
                return {}
        return {}
    
    def _save_api_keys(self):
        """Save API keys to file."""
        try:
            with open(self.api_keys_file, 'w', encoding='utf-8') as f:
                json.dump(self.api_keys, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving API keys: {e}")
    
    def generate_api_key(self, name: str, description: str = None) -> str:
        """Generate a new API key."""
        # Generate a secure random API key
        key = f"sk-nutrition-{secrets.token_urlsafe(32)}"
        
        # Store key info
        self.api_keys[key] = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "active": True,
            "usage_count": 0,
            "last_used": None
        }
        
        self._save_api_keys()
        logger.info(f"Generated new API key for: {name}")
        return key
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate an API key."""
        if api_key not in self.api_keys:
            return False
        
        key_info = self.api_keys[api_key]
        if not key_info.get("active", False):
            return False
        
        # Update usage statistics
        key_info["usage_count"] = key_info.get("usage_count", 0) + 1
        key_info["last_used"] = datetime.now().isoformat()
        self._save_api_keys()
        
        return True
    
    def deactivate_api_key(self, api_key: str) -> bool:
        """Deactivate an API key."""
        if api_key in self.api_keys:
            self.api_keys[api_key]["active"] = False
            self._save_api_keys()
            logger.info(f"Deactivated API key: {api_key}")
            return True
        return False
    
    def list_api_keys(self) -> List[Dict]:
        """List all API keys (without revealing the actual keys)."""
        result = []
        for key, info in self.api_keys.items():
            result.append({
                "key_id": key[:20] + "...",
                "name": info["name"],
                "description": info.get("description"),
                "created_at": info["created_at"],
                "active": info["active"],
                "usage_count": info.get("usage_count", 0),
                "last_used": info.get("last_used")
            })
        return result
    
    def get_key_info(self, api_key: str) -> Optional[Dict]:
        """Get information about a specific API key."""
        return self.api_keys.get(api_key)

# Global instance
auth_service = AuthService()

# Generate a default API key if none exist
if not auth_service.api_keys:
    default_key = auth_service.generate_api_key(
        "Default Key", 
        "Default API key for testing"
    )
    print(f"🔑 Generated default API key: {default_key}")
    print("⚠️  Save this key! You'll need it to access the API.")