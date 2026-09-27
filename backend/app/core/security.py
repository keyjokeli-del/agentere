import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Request, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ph = PasswordHasher()

# Config
JWT_SECRET = os.getenv("JWT_SECRET", "lumina_jwt_super_secret_key_2026_clinic_secure")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))
ADMIN_PIN = os.getenv("ADMIN_PIN", "2026")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "lumina_admin_2026")

# In-memory pre-hashed admin PIN for fast constant-time verification
_ADMIN_PIN_HASH = ph.hash(ADMIN_PIN)

# In-memory brute force tracker: ip -> list of failure timestamps
_failed_attempts: Dict[str, List[float]] = {}

security_bearer = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    """Extracts client IP considering reverse proxies (Render, Cloudflare, etc.)."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "127.0.0.1"


def verify_pin_argon2id(pin: str) -> bool:
    """Verifies PIN against the argon2id hash of ADMIN_PIN."""
    try:
        current_admin_pin = os.getenv("ADMIN_PIN", "2026")
        # If env changed dynamically, refresh hash
        global _ADMIN_PIN_HASH
        if current_admin_pin != ADMIN_PIN:
            _ADMIN_PIN_HASH = ph.hash(current_admin_pin)
        return ph.verify(_ADMIN_PIN_HASH, pin)
    except (VerifyMismatchError, VerificationError):
        return False
    except Exception:
        # Fallback check
        return pin == os.getenv("ADMIN_PIN", "2026")


def check_brute_force(ip: str) -> Optional[int]:
    """
    Checks if an IP is temporarily locked out due to failed attempts.
    Returns the number of seconds remaining in lockout, or None if allowed.
    Backoff policy:
      - 5 to 9 failed attempts: 1 minute (60s)
      - 10 to 14 failed attempts: 5 minutes (300s)
      - 15+ failed attempts: 15 minutes (900s)
    """
    now = time.time()
    attempts = _failed_attempts.get(ip, [])
    # Filter attempts within the last 15 minutes (900s)
    recent = [t for t in attempts if now - t < 900]
    _failed_attempts[ip] = recent

    count = len(recent)
    if count >= 15:
        last = recent[-1]
        remaining = int(900 - (now - last))
        if remaining > 0:
            return remaining
    elif count >= 10:
        last = recent[-1]
        remaining = int(300 - (now - last))
        if remaining > 0:
            return remaining
    elif count >= 5:
        last = recent[-1]
        remaining = int(60 - (now - last))
        if remaining > 0:
            return remaining

    return None


def record_failed_attempt(ip: str):
    """Records a failed authentication attempt timestamp for an IP."""
    now = time.time()
    if ip not in _failed_attempts:
        _failed_attempts[ip] = []
    _failed_attempts[ip].append(now)


def reset_brute_force(ip: str):
    """Resets failed attempts upon successful login."""
    _failed_attempts.pop(ip, None)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT with HS256."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decodes and validates a JWT token."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


async def verify_admin_jwt(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)
) -> dict:
    """
    Dependency that enforces admin authentication.
    Accepts:
      1. Authorization: Bearer <JWT>
      2. Cookie: lumina_auth_token=<JWT>
      3. Header: X-Admin-Key: <ADMIN_API_KEY> (backwards compatibility)
    """
    # 1. Check Bearer token from header
    token = None
    if auth_header and auth_header.credentials:
        token = auth_header.credentials
    elif "authorization" in request.headers:
        header_val = request.headers["authorization"]
        if header_val.lower().startswith("bearer "):
            token = header_val[7:].strip()

    # 2. Check HttpOnly cookie
    if not token:
        token = request.cookies.get("lumina_auth_token")

    # 3. Check query parameters (for EventSource SSE streams and WebSocket connections)
    if not token:
        token = request.query_params.get("token")

    if token:
        try:
            payload = decode_access_token(token)
            if payload.get("sub") == "admin":
                return payload
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token subject invalid"
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

    # 3. Check X-Admin-Key header (backwards compatibility for existing test suite and internal callers)
    admin_key_header = request.headers.get("x-admin-key")
    expected_key = os.getenv("ADMIN_API_KEY", "lumina_admin_2026")
    if admin_key_header and admin_key_header == expected_key:
        return {"sub": "admin", "auth_method": "api_key"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Admin authentication required via Bearer JWT, HttpOnly cookie, or X-Admin-Key"
    )


# Public Aliases & Convenience Helpers (Mejora 1 & 20)
verify_admin_pin = verify_pin_argon2id
create_admin_jwt = create_access_token
decode_admin_jwt = decode_access_token
reset_failed_attempts = reset_brute_force
failed_attempts = _failed_attempts


def record_attempt_and_check_lockout(ip: str):
    """Checks existing lockout and records a failure, raising HTTP 429 if threshold is reached."""
    lock_remaining = check_brute_force(ip)
    if lock_remaining:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Bloqueo temporal por seguridad. Reintenta en {lock_remaining} segundos."
        )
    record_failed_attempt(ip)
    new_lock = check_brute_force(ip)
    if new_lock:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Bloqueo temporal por seguridad. Reintenta en {new_lock} segundos."
        )

