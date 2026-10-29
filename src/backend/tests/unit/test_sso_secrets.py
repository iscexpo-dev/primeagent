"""Tests for the versioned SSO client-secret encryption contract."""

from types import SimpleNamespace

import pytest
from primeagent.services.database.models import (
    SSOSecretError,
    decrypt_sso_client_secret,
    encrypt_sso_client_secret,
    is_sso_client_secret_envelope,
)
from pydantic import SecretStr

_PLAINTEXT = "downstream-oidc-client-secret"
_DEFAULT_SECRET_KEY = "unit-test-primeagent-secret-key-material"  # noqa: S105  # pragma: allowlist secret


def _settings(secret_key: str | None = None):
    return SimpleNamespace(auth_settings=SimpleNamespace(SECRET_KEY=SecretStr(secret_key or _DEFAULT_SECRET_KEY)))


def test_sso_client_secret_round_trip_uses_versioned_envelope():
    encrypted = encrypt_sso_client_secret(_PLAINTEXT, _settings())

    assert decrypt_sso_client_secret(encrypted, _settings()) == _PLAINTEXT
    assert _PLAINTEXT not in encrypted
    assert encrypted.startswith("lf-sso:v1:hkdf-sha256-v1:aes-256-gcm:")


def test_sso_client_secret_defaults_to_existing_primeagent_secret_key(monkeypatch):
    from primeagent.services import deps

    settings = _settings()
    monkeypatch.setattr(deps, "get_settings_service", lambda: settings)

    encrypted = encrypt_sso_client_secret(_PLAINTEXT)

    assert decrypt_sso_client_secret(encrypted) == _PLAINTEXT


def test_sso_client_secret_encryption_uses_random_nonces():
    first = encrypt_sso_client_secret(_PLAINTEXT, _settings())
    second = encrypt_sso_client_secret(_PLAINTEXT, _settings())

    assert first != second
    assert decrypt_sso_client_secret(first, _settings()) == _PLAINTEXT
    assert decrypt_sso_client_secret(second, _settings()) == _PLAINTEXT


def test_sso_client_secret_rejects_wrong_primeagent_secret_key():
    encrypted = encrypt_sso_client_secret(_PLAINTEXT, _settings("original-primeagent-secret-key"))

    with pytest.raises(SSOSecretError, match="PRIMEAGENT_SECRET_KEY"):
        decrypt_sso_client_secret(encrypted, _settings("different-primeagent-secret-key"))


@pytest.mark.parametrize("client_secret", ["", " ", "\t\n"])
def test_sso_client_secret_rejects_blank_plaintext(client_secret):
    with pytest.raises(SSOSecretError, match="must not be blank"):
        encrypt_sso_client_secret(client_secret, _settings())


def test_sso_client_secret_rejects_unknown_envelope_version():
    encrypted = encrypt_sso_client_secret(_PLAINTEXT, _settings())
    unknown_version = encrypted.replace(":v1:", ":v2:", 1)

    with pytest.raises(SSOSecretError, match="version"):
        decrypt_sso_client_secret(unknown_version, _settings())


@pytest.mark.parametrize("invalid_character", ["!", "+", "/", "="])
@pytest.mark.parametrize("payload_index", [4, 5], ids=["nonce", "ciphertext"])
def test_sso_client_secret_rejects_non_base64url_payload_characters(invalid_character, payload_index):
    encrypted = encrypt_sso_client_secret(_PLAINTEXT, _settings())
    parts = encrypted.split(":")
    parts[payload_index] = f"{invalid_character}{parts[payload_index][1:]}"
    malformed = ":".join(parts)

    assert not is_sso_client_secret_envelope(malformed)
    with pytest.raises(SSOSecretError, match="Invalid base64url data"):
        decrypt_sso_client_secret(malformed, _settings())


@pytest.mark.parametrize("payload_index", [4, 5], ids=["nonce", "ciphertext"])
def test_sso_client_secret_rejects_empty_payload(payload_index):
    encrypted = encrypt_sso_client_secret(_PLAINTEXT, _settings())
    parts = encrypted.split(":")
    parts[payload_index] = ""
    malformed = ":".join(parts)

    assert not is_sso_client_secret_envelope(malformed)
    with pytest.raises(SSOSecretError, match="Invalid base64url data"):
        decrypt_sso_client_secret(malformed, _settings())
