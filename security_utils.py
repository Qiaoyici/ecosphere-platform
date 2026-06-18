import os
import hmac
import hashlib
import base64
import json
import html
from typing import Dict, Any, Tuple

# Retrieve the signature key dynamically from environment configuration
SECRET_KEY = os.getenv(
    "ECOSPHERE_SECRET",
    "ecosphere_secret_secure_key_2026_promptwars"
).encode("utf-8")

def sanitize_string(text: str) -> str:
    """Escapes HTML special characters to prevent cross-site scripting (XSS).

    Args:
        text: The raw input string to escape.

    Returns:
        The sanitized and trimmed string, or an empty string if input is invalid.
    """
    if not isinstance(text, str):
        return ""
    return html.escape(text.strip())

def encrypt_and_sign_state(state: Dict[str, Any]) -> Dict[str, str]:
    """Serializes deterministically, encodes to Base64, and signs client state.

    Args:
        state: A dictionary containing the client state to encrypt and sign.

    Returns:
        A dictionary containing the encoded 'payload' and the HMAC SHA256 'signature'.
    """
    try:
        serialized = json.dumps(state, sort_keys=True)
        encoded_payload = base64.b64encode(serialized.encode('utf-8')).decode('utf-8')
        signature = hmac.new(
            SECRET_KEY,
            encoded_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "payload": encoded_payload,
            "signature": signature
        }
    except Exception as e:
        return {"error": "Encryption failed", "message": str(e)}

def decrypt_and_verify_state(payload: str, signature: str) -> Tuple[bool, Dict[str, Any]]:
    """Verifies the HMAC signature and decrypts the Base64 state payload.

    Args:
        payload: The Base64 encoded state payload string.
        signature: The expected HMAC SHA256 signature hash.

    Returns:
        A tuple of (success_status, decrypted_data).
    """
    try:
        expected_sig = hmac.new(
            SECRET_KEY,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            return False, {"error": "Tamper detected: signature mismatch."}
        
        decoded_bytes = base64.b64decode(payload.encode('utf-8'))
        state_data = json.loads(decoded_bytes.decode('utf-8'))
        return True, state_data
    except Exception as e:
        return False, {"error": "Decryption failed", "message": str(e)}

def validate_numeric_input(
    value: Any,
    min_val: float = 0.0,
    max_val: float = 1000000.0
) -> float:
    """Validates and clamps numeric inputs to prevent negative or overflow values.

    Args:
        value: The raw input to parse and validate.
        min_val: The minimum allowed value (default 0.0).
        max_val: The maximum allowed value (default 1,000,000.0).

    Returns:
        The validated float value, clamped between min_val and max_val,
        or 0.0 if parsing fails.
    """
    try:
        num = float(value)
        if num < min_val:
            return min_val
        if num > max_val:
            return max_val
        return num
    except (TypeError, ValueError):
        return 0.0


