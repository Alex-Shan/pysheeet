"""
Tests for modern cryptography examples.
"""

import hashlib
import hmac
import os
import secrets

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ed25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import (
    AESGCM,
    ChaCha20Poly1305,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class TestSecureRandom:
    """Test secure random generation."""

    def test_token_bytes(self):
        key = secrets.token_bytes(32)
        assert len(key) == 32
        # 每次应该不一样
        assert key != secrets.token_bytes(32)

    def test_token_urlsafe(self):
        token = secrets.token_urlsafe(32)
        assert len(token) >= 32  # Base64 encoding 使其更长

    def test_token_hex(self):
        token = secrets.token_hex(16)
        assert len(token) == 32  # 16 bytes = 32 hex chars

    def test_randbelow(self):
        for _ in range(100):
            n = secrets.randbelow(100)
            assert 0 <= n < 100


class TestHashing:
    """Test cryptographic hashing."""

    def test_sha256(self):
        data = b"Hello, World!"
        digest = hashlib.sha256(data).hexdigest()
        assert len(digest) == 64  # 256 bits = 64 hex chars
        # Same input = same output
        assert digest == hashlib.sha256(data).hexdigest()

    def test_sha3_256(self):
        data = b"Hello, World!"
        digest = hashlib.sha3_256(data).hexdigest()
        assert len(digest) == 64

    def test_blake2b(self):
        data = b"Hello, World!"
        digest = hashlib.blake2b(data, digest_size=32).hexdigest()
        assert len(digest) == 64

    def test_blake2b_keyed(self):
        data = b"Hello, World!"
        key = b"secret-key-here!"
        mac = hashlib.blake2b(data, key=key, digest_size=32).hexdigest()
        assert len(mac) == 64
        # Different key = different MAC
        other_mac = hashlib.blake2b(
            data, key=b"other-key-here!!", digest_size=32
        ).hexdigest()
        assert mac != other_mac


class TestHMAC:
    """Test HMAC operations."""

    def test_hmac_create_verify(self):
        key = secrets.token_bytes(32)
        message = b"Important message"
        mac = hmac.new(key, message, hashlib.sha256).digest()
        assert hmac.compare_digest(
            mac, hmac.new(key, message, hashlib.sha256).digest()
        )

    def test_hmac_tamper_detection(self):
        key = secrets.token_bytes(32)
        message = b"Important message"
        mac = hmac.new(key, message, hashlib.sha256).digest()
        tampered = b"Tampered message"
        tampered_mac = hmac.new(key, tampered, hashlib.sha256).digest()
        assert not hmac.compare_digest(mac, tampered_mac)


class TestKeyDerivation:
    """Test key derivation functions."""

    def test_pbkdf2(self):
        password = b"user-password"
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,  # 较低的测试
        )
        key = kdf.derive(password)
        assert len(key) == 32

    def test_pbkdf2_verify(self):
        password = b"user-password"
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = kdf.derive(password)

        # 使用新的 KDF instance 进行验证
        kdf2 = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        kdf2.verify(password, key)  # 不应该提高

    def test_hkdf(self):
        master_key = os.urandom(32)
        salt = os.urandom(16)
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"encryption-key",
        )
        derived = hkdf.derive(master_key)
        assert len(derived) == 32


class TestAESGCM:
    """Test AES-GCM authenticated encryption."""

    def test_encrypt_decrypt(self):
        key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        plaintext = b"Secret message"
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        assert decrypted == plaintext

    def test_with_associated_data(self):
        key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        plaintext = b"Secret message"
        aad = b"header"
        ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
        decrypted = aesgcm.decrypt(nonce, ciphertext, aad)
        assert decrypted == plaintext

    def test_tamper_detection(self):
        key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        plaintext = b"Secret message"
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        tampered = bytearray(ciphertext)
        tampered[0] ^= 1
        with pytest.raises(Exception):
            aesgcm.decrypt(nonce, bytes(tampered), None)


class TestChaCha20Poly1305:
    """Test ChaCha20-Poly1305 authenticated encryption."""

    def test_encrypt_decrypt(self):
        key = ChaCha20Poly1305.generate_key()
        chacha = ChaCha20Poly1305(key)
        nonce = os.urandom(12)
        plaintext = b"Secret message"
        ciphertext = chacha.encrypt(nonce, plaintext, None)
        decrypted = chacha.decrypt(nonce, ciphertext, None)
        assert decrypted == plaintext


class TestFernet:
    """Test Fernet high-level encryption."""

    def test_encrypt_decrypt(self):
        key = Fernet.generate_key()
        f = Fernet(key)
        plaintext = b"Secret message"
        token = f.encrypt(plaintext)
        decrypted = f.decrypt(token)
        assert decrypted == plaintext

    def test_different_tokens(self):
        key = Fernet.generate_key()
        f = Fernet(key)
        plaintext = b"Secret message"
        token1 = f.encrypt(plaintext)
        token2 = f.encrypt(plaintext)
        # 相同的明文产生不同的令牌（随机IV）
        assert token1 != token2


class TestRSA:
    """Test RSA operations."""

    def test_key_generation(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        assert private_key is not None
        assert public_key is not None

    def test_key_serialization(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        assert pem.startswith(b"-----BEGIN PRIVATE KEY-----")

    def test_oaep_encrypt_decrypt(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        plaintext = b"Secret message"
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        decrypted = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        assert decrypted == plaintext

    def test_pss_sign_verify(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        message = b"Message to sign"
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        # 不应该提高
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )


class TestEd25519:
    """Test Ed25519 signatures."""

    def test_sign_verify(self):
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        message = b"Message to sign"
        signature = private_key.sign(message)
        # 不应该提高
        public_key.verify(signature, message)

    def test_invalid_signature(self):
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        message = b"Message to sign"
        signature = private_key.sign(message)
        with pytest.raises(Exception):
            public_key.verify(signature, b"Different message")


class TestX25519:
    """Test X25519 key exchange."""

    def test_key_exchange(self):
        alice_private = X25519PrivateKey.generate()
        alice_public = alice_private.public_key()
        bob_private = X25519PrivateKey.generate()
        bob_public = bob_private.public_key()

        alice_shared = alice_private.exchange(bob_public)
        bob_shared = bob_private.exchange(alice_public)

        assert alice_shared == bob_shared
        assert len(alice_shared) == 32


class TestHybridEncryption:
    """Test hybrid RSA + AES-GCM encryption."""

    def test_hybrid_encrypt_decrypt(self):
        def hybrid_encrypt(public_key, plaintext):
            aes_key = AESGCM.generate_key(bit_length=256)
            nonce = os.urandom(12)
            aesgcm = AESGCM(aes_key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            encrypted_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return encrypted_key, nonce, ciphertext

        def hybrid_decrypt(private_key, encrypted_key, nonce, ciphertext):
            aes_key = private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            aesgcm = AESGCM(aes_key)
            return aesgcm.decrypt(nonce, ciphertext, None)

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        message = b"This is a longer message that exceeds RSA limits" * 100
        encrypted_key, nonce, ciphertext = hybrid_encrypt(public_key, message)
        decrypted = hybrid_decrypt(
            private_key, encrypted_key, nonce, ciphertext
        )
        assert decrypted == message
