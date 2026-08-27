"""
APM Security Module

Copyright (c) Vidyut Prabakaran — MIT License
"""

import os
import json
import hashlib
import hmac
import base64
import bcrypt
from cryptography.fernet import Fernet, InvalidToken


PBKDF2_ITERATIONS = 600_000       # OWASP 2023 recommendation for HMAC-SHA256
SALT_LENGTH = 32                  # 256-bit random salt
BCRYPT_COST = 12                  # bcrypt work factor
CREDENTIAL_FORMAT_VERSION = 2     # current secure format version

_LEGACY_HARDCODED_KEY = b'A8bpuzskrccSJLQ-ZCb5nKzRbO1ia3JnKtrTa65NESE='


def hash_master_password(password: str) -> bytes:

    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=BCRYPT_COST))


def verify_master_password(password: str, stored_hash: bytes) -> bool:

    try:
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    except (ValueError, TypeError):
        return False


def derive_key(password: str, salt: bytes = None) -> tuple:

    if salt is None:
        salt = os.urandom(SALT_LENGTH)

    raw_key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        PBKDF2_ITERATIONS,
        dklen=32,
    )
    # Fernet requires a url-safe base64-encoded 32-byte key
    fernet_key = base64.urlsafe_b64encode(raw_key)
    return fernet_key, salt


def make_fernet(password: str, salt: bytes = None) -> tuple:
    """Convenience: derive key and return a ready-to-use Fernet instance + salt."""
    fernet_key, salt = derive_key(password, salt)
    return Fernet(fernet_key), salt

def encrypt_credential(plaintext: str, fernet: Fernet) -> str:
    """Encrypt a credential value.  Returns a base64-encoded ciphertext string."""
    return fernet.encrypt(plaintext.encode('utf-8')).decode('ascii')


def decrypt_credential(ciphertext: str, fernet: Fernet) -> str:
    """Decrypt a credential value.  Raises InvalidToken on failure."""
    if isinstance(ciphertext, str):
        ciphertext = ciphertext.encode('ascii')
    return fernet.decrypt(ciphertext).decode('utf-8')

def compute_hmac(data: bytes, key: bytes) -> str:
    """Compute HMAC-SHA256 over *data* using *key*.  Returns hex digest."""
    return hmac.new(key, data, hashlib.sha256).hexdigest()


def verify_hmac(data: bytes, key: bytes, expected: str) -> bool:
    """Constant-time HMAC verification to prevent timing attacks."""
    return hmac.compare_digest(compute_hmac(data, key), expected)

def save_credentials_secure(
    credentials: dict,
    fernet: Fernet,
    fernet_key: bytes,
    salt: bytes,
    filepath: str,
) -> None:
    encrypted = {}
    for account, password in credentials.items():
        encrypted[account] = encrypt_credential(password, fernet)

    payload = {
        'version': CREDENTIAL_FORMAT_VERSION,
        'salt': salt.hex(),
        'credentials': encrypted,
    }

    # Compute HMAC over the payload (without the hmac field itself)
    payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
    payload['hmac'] = compute_hmac(payload_bytes, fernet_key)

    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)


def load_credentials_secure(
    filepath: str,
    password: str,
) -> tuple:

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if data.get('version') != CREDENTIAL_FORMAT_VERSION:
        raise ValueError(f"Unknown credential format version: {data.get('version')}")

    salt = bytes.fromhex(data['salt'])
    fernet_key, _ = derive_key(password, salt)
    fernet = Fernet(fernet_key)

    # Verify HMAC
    stored_hmac = data.pop('hmac', '')
    payload_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
    if not verify_hmac(payload_bytes, fernet_key, stored_hmac):
        raise ValueError("Credential file integrity check failed — file may have been tampered with.")

    # Decrypt
    credentials = {}
    for account, ciphertext in data.get('credentials', {}).items():
        credentials[account] = decrypt_credential(ciphertext, fernet)

    return credentials, fernet, fernet_key, salt


# ---------------------------------------------------------------------------
# Legacy Migration
# ---------------------------------------------------------------------------

def _try_decrypt_legacy(
    ciphertext,
    legacy_fernet,
    hardcoded_fernet,
) -> str:

    # Ensure we're working with bytes
    if isinstance(ciphertext, str):
        ciphertext = ciphertext.encode('ascii')

    # Try the per-install random key (fer.apm)
    if legacy_fernet is not None:
        try:
            return legacy_fernet.decrypt(ciphertext).decode('utf-8')
        except (InvalidToken, Exception):
            pass

    # Try the hardcoded default key
    try:
        return hardcoded_fernet.decrypt(ciphertext).decode('utf-8')
    except (InvalidToken, Exception):
        pass

    # Treat as unencrypted plaintext
    try:
        if isinstance(ciphertext, bytes):
            return ciphertext.decode('utf-8')
        return str(ciphertext)
    except Exception:
        return None


def detect_legacy_mp(mp_filepath: str) -> str:
    try:
        # Try reading as text first (legacy plaintext format)
        with open(mp_filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # If it starts with $2b$ or $2a$, it's already bcrypt-hashed
        if content.startswith('$2b$') or content.startswith('$2a$'):
            return None

        return content if content else None
    except FileNotFoundError:
        return None
    except Exception:
        # Try binary read (might be bcrypt bytes)
        try:
            with open(mp_filepath, 'rb') as f:
                content = f.read().strip()
            if content.startswith(b'$2b$') or content.startswith(b'$2a$'):
                return None
            return content.decode('utf-8')
        except Exception:
            return None


def load_legacy_credentials_pickle(filepath: str) -> dict:

    try:
        import pickle
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError, Exception):
        return {}


def load_legacy_credentials_json(filepath: str) -> dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Old JSON format stored values as strings (Fernet ciphertext)
        return {k: v.encode('ascii') if isinstance(v, str) else v for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return {}


def migrate_legacy_to_secure(
    master_password: str,
    mp_filepath: str,
    fer_filepath: str,
    pickle_filepath: str,
    old_json_filepath: str,
    new_cred_filepath: str,
) -> tuple:

    # 1. Hash and save the master password
    mp_hash = hash_master_password(master_password)
    os.makedirs(os.path.dirname(mp_filepath) or '.', exist_ok=True)
    with open(mp_filepath, 'wb') as f:
        f.write(mp_hash)

    # 2. Load legacy Fernet key (if exists)
    legacy_fernet = None
    try:
        with open(fer_filepath, 'rb') as f:
            legacy_key = f.read()
        if len(legacy_key) == 44:
            legacy_fernet = Fernet(legacy_key)
    except (FileNotFoundError, Exception):
        pass

    hardcoded_fernet = Fernet(_LEGACY_HARDCODED_KEY)

    # 3. Load legacy credentials (try pickle first, then old JSON)
    legacy_creds = load_legacy_credentials_pickle(pickle_filepath)
    if not legacy_creds:
        legacy_creds = load_legacy_credentials_json(old_json_filepath)

    # 4. Decrypt all legacy credentials to plaintext
    plaintext_creds = {}
    for account, ciphertext in legacy_creds.items():
        decrypted = _try_decrypt_legacy(ciphertext, legacy_fernet, hardcoded_fernet)
        if decrypted is not None:
            plaintext_creds[account] = decrypted

    # 5. Create new secure encryption
    fernet, salt = make_fernet(master_password)
    fernet_key, _ = derive_key(master_password, salt)

    # 6. Save in new secure format
    save_credentials_secure(plaintext_creds, fernet, fernet_key, salt, new_cred_filepath)

    # 7. Clean up old files
    for old_file in [fer_filepath, pickle_filepath]:
        try:
            if os.path.exists(old_file):
                os.remove(old_file)
        except Exception:
            pass

    # Also remove old JSON if it's different from the new path
    if old_json_filepath != new_cred_filepath:
        try:
            if os.path.exists(old_json_filepath):
                os.remove(old_json_filepath)
        except Exception:
            pass

    return plaintext_creds, fernet, fernet_key, salt


def is_secure_format(filepath: str) -> bool:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('version') == CREDENTIAL_FORMAT_VERSION
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return False


def is_mp_hashed(mp_filepath: str) -> bool:
    try:
        with open(mp_filepath, 'rb') as f:
            content = f.read().strip()
        return content.startswith(b'$2b$') or content.startswith(b'$2a$')
    except (FileNotFoundError, Exception):
        return False
