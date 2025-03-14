"""
oauth2.py - Independent OAuth 2.0 Client Implementation
A standalone Python module for OAuth 2.0 authentication flows.
"""

import base64
import json
import time
import urllib.parse
import uuid
from typing import Dict, List, Optional, Tuple, Union, Any

import requests


class OAuth2Error(Exception):
    """Base exception for OAuth2 errors."""
    pass


class TokenError(OAuth2Error):
    """Exception raised for token-related errors."""
    pass


class OAuth2Client:
    """
    OAuth2 client implementation supporting various grant types:
    - Authorization Code (with PKCE support)
    - Client Credentials
    - Resource Owner Password Credentials
    - Refresh Token
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: Optional[str] = None,
        token_url: Optional[str] = None,
        auth_url: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scope: Optional[List[str]] = None,
        token_storage: Optional["TokenStorage"] = None,
    ):
        """
        Initialize OAuth2 client with the required parameters.
        
        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret (optional for some flows)
            token_url: Token endpoint URL
            auth_url: Authorization endpoint URL (for authorization code flow)
            redirect_uri: Redirect URI (for authorization code flow)
            scope: List of scope strings
            token_storage: Optional token storage implementation
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.auth_url = auth_url
        self.redirect_uri = redirect_uri
        self.scope = scope or []
        self.token_storage = token_storage or InMemoryTokenStorage()
        
        # For PKCE
        self._code_verifier = None
    
    def create_authorization_url(self, state: Optional[str] = None, use_pkce: bool = True, **kwargs) -> Tuple[str, str]:
        """
        Create an authorization URL for the authorization code flow.
        
        Args:
            state: Optional state parameter (generated if not provided)
            use_pkce: Whether to use PKCE (Proof Key for Code Exchange)
            **kwargs: Additional parameters to include in the authorization URL
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if not self.auth_url:
            raise OAuth2Error("Authorization URL not provided")
            
        if not self.redirect_uri:
            raise OAuth2Error("Redirect URI not provided")
        
        if not state:
            state = str(uuid.uuid4())
            
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
        }
        
        if self.scope:
            params["scope"] = " ".join(self.scope)
            
        # Add PKCE parameters if requested
        if use_pkce:
            self._code_verifier = self._generate_code_verifier()
            params["code_challenge"] = self._generate_code_challenge(self._code_verifier)
            params["code_challenge_method"] = "S256"
            
        # Add any additional parameters
        params.update(kwargs)
            
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(params)}"
        return auth_url, state
    
    def fetch_token(
        self,
        code: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        grant_type: str = "authorization_code",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch an access token using the specified grant type.
        
        Args:
            code: Authorization code (for authorization_code grant)
            username: Username (for password grant)
            password: Password (for password grant)
            grant_type: OAuth2 grant type
            **kwargs: Additional parameters to include in the token request
            
        Returns:
            Dict containing token information
        """
        if not self.token_url:
            raise OAuth2Error("Token URL not provided")
            
        data = {
            "grant_type": grant_type,
            "client_id": self.client_id,
        }
        
        # Add client secret if available
        auth = None
        if self.client_secret:
            if grant_type != "authorization_code" or not kwargs.get("use_basic_auth", False):
                data["client_secret"] = self.client_secret
            else:
                # Use HTTP Basic auth
                auth = (self.client_id, self.client_secret)
                
        # Add parameters based on grant type
        if grant_type == "authorization_code":
            if not code:
                raise OAuth2Error("Authorization code required")
                
            data["code"] = code
            data["redirect_uri"] = self.redirect_uri
            
            # Add PKCE code verifier if available
            if self._code_verifier:
                data["code_verifier"] = self._code_verifier
                self._code_verifier = None
                
        elif grant_type == "password":
            if not username or not password:
                raise OAuth2Error("Username and password required for password grant")
                
            data["username"] = username
            data["password"] = password
            
            if self.scope:
                data["scope"] = " ".join(self.scope)
                
        elif grant_type == "client_credentials":
            if self.scope:
                data["scope"] = " ".join(self.scope)
                
        elif grant_type == "refresh_token":
            if not kwargs.get("refresh_token"):
                # Try to get from storage
                stored_token = self.token_storage.get_token()
                if not stored_token or "refresh_token" not in stored_token:
                    raise OAuth2Error("Refresh token required")
                data["refresh_token"] = stored_token["refresh_token"]
            else:
                data["refresh_token"] = kwargs.pop("refresh_token")
        
        # Add any additional parameters
        data.update(kwargs)
        
        # Make the token request
        headers = {"Accept": "application/json"}
        
        response = requests.post(
            self.token_url, 
            data=data, 
            headers=headers, 
            auth=auth,
            timeout=30
        )
        
        if response.status_code != 200:
            error_desc = "Unknown error"
            try:
                error_data = response.json()
                error_desc = error_data.get("error_description", error_data.get("error", "Unknown error"))
            except:
                if response.text:
                    error_desc = response.text
            
            raise TokenError(f"Error fetching token: {error_desc} (HTTP {response.status_code})")
            
        token_data = response.json()
        
        # Add expiration timestamp if expires_in is provided
        if "expires_in" in token_data and "expires_at" not in token_data:
            token_data["expires_at"] = time.time() + int(token_data["expires_in"])
            
        # Store the token
        self.token_storage.save_token(token_data)
        
        return token_data
    
    def refresh_token(self, refresh_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token (optional, retrieved from storage if not provided)
            
        Returns:
            Dict containing new token information
        """
        return self.fetch_token(grant_type="refresh_token", refresh_token=refresh_token)
    
    def get_token(self, auto_refresh: bool = True) -> Dict[str, Any]:
        """
        Get the current token, refreshing if necessary and auto_refresh is True.
        
        Args:
            auto_refresh: Whether to automatically refresh an expired token
            
        Returns:
            Dict containing token information
        """
        token = self.token_storage.get_token()
        
        if not token:
            raise TokenError("No token available")
            
        if auto_refresh and self._is_token_expired(token):
            try:
                token = self.refresh_token()
            except OAuth2Error as e:
                raise TokenError(f"Failed to refresh token: {e}")
                
        return token
    
    def get_access_token(self, auto_refresh: bool = True) -> str:
        """
        Get just the access token string.
        
        Args:
            auto_refresh: Whether to automatically refresh an expired token
            
        Returns:
            Access token string
        """
        token = self.get_token(auto_refresh=auto_refresh)
        return token["access_token"]
    
    def _is_token_expired(self, token: Dict[str, Any]) -> bool:
        """Check if the token is expired."""
        if "expires_at" not in token:
            return False
            
        # Add a buffer of 10 seconds to ensure we don't use a token that's about to expire
        return token["expires_at"] <= time.time() + 10
    
    def _generate_code_verifier(self, length: int = 64) -> str:
        """Generate a code verifier for PKCE."""
        import secrets
        return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode('utf-8').rstrip('=')
    
    def _generate_code_challenge(self, verifier: str) -> str:
        """Generate a code challenge from the code verifier."""
        import hashlib
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')


class TokenStorage:
    """Base class for token storage implementations."""
    
    def save_token(self, token: Dict[str, Any]) -> None:
        """Save a token."""
        raise NotImplementedError
        
    def get_token(self) -> Optional[Dict[str, Any]]:
        """Get the stored token."""
        raise NotImplementedError
        
    def delete_token(self) -> None:
        """Delete the stored token."""
        raise NotImplementedError


class InMemoryTokenStorage(TokenStorage):
    """Simple in-memory token storage."""
    
    def __init__(self):
        self.token = None
        
    def save_token(self, token: Dict[str, Any]) -> None:
        """Save a token in memory."""
        self.token = token
        
    def get_token(self) -> Optional[Dict[str, Any]]:
        """Get the stored token."""
        return self.token
        
    def delete_token(self) -> None:
        """Delete the stored token."""
        self.token = None


class FileTokenStorage(TokenStorage):
    """File-based token storage."""
    
    def __init__(self, file_path: str):
        """
        Initialize file token storage.
        
        Args:
            file_path: Path to the token file
        """
        self.file_path = file_path
        
    def save_token(self, token: Dict[str, Any]) -> None:
        """Save a token to file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(token, f)
        except Exception as e:
            raise OAuth2Error(f"Failed to save token to file: {e}")
        
    def get_token(self) -> Optional[Dict[str, Any]]:
        """Get the token from file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            raise OAuth2Error(f"Failed to read token from file: {e}")
        
    def delete_token(self) -> None:
        """Delete the token file."""
        import os
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
        except Exception as e:
            raise OAuth2Error(f"Failed to delete token file: {e}")


class OAuth2Session:
    """
    A requests-like session with automatic OAuth2 authentication.
    """
    
    def __init__(self, client: OAuth2Client):
        """
        Initialize OAuth2 session.
        
        Args:
            client: OAuth2Client instance
        """
        self.client = client
        self.session = requests.Session()
        
    def request(
        self, 
        method: str, 
        url: str, 
        auto_refresh: bool = True, 
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request with OAuth2 authentication.
        
        Args:
            method: HTTP method
            url: URL to request
            auto_refresh: Whether to automatically refresh an expired token
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            requests.Response object
        """
        headers = kwargs.pop('headers', {})
        
        # Get access token
        token = self.client.get_token(auto_refresh=auto_refresh)
        
        # Add authorization header
        headers['Authorization'] = f"{token.get('token_type', 'Bearer')} {token['access_token']}"
        
        # Make the request
        return self.session.request(method, url, headers=headers, **kwargs)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make a GET request."""
        return self.request('GET', url, **kwargs)
        
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make a POST request."""
        return self.request('POST', url, **kwargs)
        
    def put(self, url: str, **kwargs) -> requests.Response:
        """Make a PUT request."""
        return self.request('PUT', url, **kwargs)
        
    def delete(self, url: str, **kwargs) -> requests.Response:
        """Make a DELETE request."""
        return self.request('DELETE', url, **kwargs)
        
    def patch(self, url: str, **kwargs) -> requests.Response:
        """Make a PATCH request."""
        return self.request('PATCH', url, **kwargs)