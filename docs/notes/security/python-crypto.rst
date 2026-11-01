.. meta::
    :description lang=zh_CN: 现代 Python 密码学指南，涵盖对称加密 (AES-GCM)、非对称加密 (RSA-OAEP)、数字签名、key 推导以及使用密码学 library 的安全随机生成
    :keywords: Python, Python3, Cryptography, AES-GCM, RSA, OAEP, Digital Signature, PBKDF2, Argon2, Key Derivation, Encryption, Decryption, HMAC, Hashing

====================================================
现代密码学（Modern Cryptography）
====================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

本指南涵盖了使用 ``cryptography`` library 的 Python 中的现代加密实践，这是新项目的推荐选择。 library 提供用于常见用例的高级配方 (Fernet) 和用于高级需求的低级原语。我们专注于安全默认值：用于对称加密的 AES-GCM（提供机密性和完整性）、用于非对称加密的 RSA-OAEP、用于签名的 Ed25519 以及正确的 key 派生 functions。避免使用像 PyCrypto 这样已弃用的 libraries，而是使用 ``cryptography`` 或 ``PyCryptodome`` 。

.. warning::

    密码学很难正确实施。尽可能选择像 Fernet 这样的高级 APIs。永远不要发明自己的加密方案。始终使用经过身份验证的加密（AES-GCM、ChaCha20-Poly1305）而不是未经身份验证的模式（单独使用 AES-CBC、AES-CTR）。

算法推荐（Algorithm Recommendations）
--------------------------------------------------------------

选择安全算法的快速参考。如有疑问，请使用推荐的选项——它们代表了截至 2024 年的当前最佳实践。

::

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    ALGORITHM RECOMMENDATIONS                            │
    ├─────────────────────────────────────────────────────────────────────────┤
    │  USE CASE              │ RECOMMENDED          │ AVOID                   │
    ├────────────────────────┼──────────────────────┼─────────────────────────┤
    │  Symmetric Encryption  │ AES-256-GCM          │ AES-CBC, AES-ECB,       │
    │                        │ ChaCha20-Poly1305    │ DES, 3DES, Blowfish,    │
    │                        │                      │ RC4                     │
    ├────────────────────────┼──────────────────────┼─────────────────────────┤
    │  Asymmetric Encryption │ RSA-OAEP (≥3072-bit) │ RSA PKCS#1 v1.5,        │
    │                        │ ECIES                │ RSA < 2048-bit,         │
    │                        │                      │ ElGamal                 │
    ├────────────────────────┼──────────────────────┼─────────────────────────┤
    │  Digital Signatures    │ Ed25519              │ RSA PKCS#1 v1.5,        │
    │                        │ RSA-PSS (≥3072-bit)  │ DSA, ECDSA with P-256   │
    │                        │ Ed448                │ (if possible)           │
    ├────────────────────────┼──────────────────────┼─────────────────────────┤
    │  Key Exchange          │ X25519               │ DH < 2048-bit,          │
    │                        │ X448                 │ Static DH               │
    │                        │ ECDH (P-384+)        │                         │
    ├────────────────────────┼──────────────────────┼─────────────────────────┤
    │  Password Hashing      │ Argon2id             │ MD5, SHA-1, SHA-256,    │
    │                        │ scrypt               │ bcrypt (less preferred),│
    │                        │ PBKDF2 (≥600k iter)  │ plain hashes            │
    ├────────────────────────┼──────────────────────┼─────────────────────────┤
    │  General Hashing       │ SHA-256, SHA-3       │ MD5, SHA-1              │
    │                        │ BLAKE2, BLAKE3       │                         │
    ├────────────────────────┼──────────────────────┼─────────────────────────┤
    │  MAC                   │ HMAC-SHA256          │ HMAC-MD5, HMAC-SHA1     │
    │                        │ KMAC, Poly1305       │                         │
    ├────────────────────────┼──────────────────────┼─────────────────────────┤
    │  Random Generation     │ secrets module       │ random module           │
    │                        │ os.urandom()         │ time-based seeds        │
    └────────────────────────┴──────────────────────┴─────────────────────────┘

密钥大小建议（Key Size Recommendations）
----------------------------------------------------------------

2030 年以后的安全最小尺寸为 key。较大的 keys 提供更多的安全裕度，但性能较慢。

::

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                       KEY SIZE GUIDELINES                               │
    ├─────────────────────────────────────────────────────────────────────────┤
    │  ALGORITHM             │ MINIMUM    │ RECOMMENDED  │ NOTES              │
    ├────────────────────────┼────────────┼──────────────┼────────────────────┤
    │  AES                   │ 128-bit    │ 256-bit      │ 256 for long-term  │
    │  ChaCha20              │ 256-bit    │ 256-bit      │ Only size available│
    │  RSA (encryption)      │ 2048-bit   │ 3072-4096    │ 4096 for long-term │
    │  RSA (signatures)      │ 2048-bit   │ 3072-4096    │ 4096 for long-term │
    │  ECDSA/ECDH            │ P-256      │ P-384        │ Prefer Ed25519     │
    │  Ed25519               │ 256-bit    │ 256-bit      │ Fixed size         │
    │  X25519                │ 256-bit    │ 256-bit      │ Fixed size         │
    │  HMAC key              │ 256-bit    │ 256-bit      │ Match hash output  │
    │  Salt (password)       │ 128-bit    │ 128-bit      │ 16 bytes minimum   │
    │  Nonce (AES-GCM)       │ 96-bit     │ 96-bit       │ 12 bytes, unique!  │
    │  IV (AES-CBC)          │ 128-bit    │ 128-bit      │ 16 bytes, random   │
    └────────────────────────┴────────────┴──────────────┴────────────────────┘

常见错误（不要这样做）（Common Mistakes (Don't Do This)）
----------------------------------------------------------------------------------------

要避免的不安全模式的示例。每个 "BAD" 示例都显示一个常见错误； "GOOD" 示例显示了安全的替代方案。

**❌ 使用随机 module 进行安全保护：**

.. code-block:: python

    # BAD：可预测的随机 - 可以进行逆向工程！
    import random
    token = ''.join(random.choices('abcdef0123456789', k=32))
    key = bytes([random.randint(0, 255) for _ in range(32)])

    # GOOD：加密安全随机
    import secrets
    token = secrets.token_hex(16)
    key = secrets.token_bytes(32)

**❌使用ECB模式：**

.. code-block:: python

    # BAD：ECB 模式揭示了数据模式！
    from Crypto.Cipher import AES
    cipher = AES.new(key, AES.MODE_ECB)  # NEVER 使用 ECB

    # GOOD：使用经过身份验证的加密
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

**❌ AES-CBC 无认证：**

.. code-block:: python

    # BAD：没有完整性检查 - 容易受到 padding 预言机攻击！
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    # 攻击者可以在不被发现的情况下修改密文！

    # GOOD：AES-GCM提供认证
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    # 解密过程中将检测到任何修改

**❌ 重用随机数：**

.. code-block:: python

    # BAD：重用随机数完全破坏了AES-GCM的安全性！
    nonce = b'fixed_nonce!'  # NEVER 这样做
    ct1 = aesgcm.encrypt(nonce, msg1, None)
    ct2 = aesgcm.encrypt(nonce, msg2, None)  # 灾难性的！

    # GOOD：为每次加密生成唯一的随机数
    import os
    nonce1 = os.urandom(12)
    ct1 = aesgcm.encrypt(nonce1, msg1, None)
    nonce2 = os.urandom(12)
    ct2 = aesgcm.encrypt(nonce2, msg2, None)

**❌ RSA 与 PKCS#1 v1.5 padding:**

.. code-block:: python

    # BAD：容易受到Bleichenbacher的攻击！
    from Crypto.Cipher import PKCS1_v1_5
    cipher = PKCS1_v1_5.new(key)
    ciphertext = cipher.encrypt(message)

    # GOOD：使用OAEP padding
    from cryptography.hazmat.primitives.asymmetric import padding
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

**❌ 使用 SHA-256:** 对密码进行哈希处理

.. code-block:: python

    # BAD：太快了——每秒数十亿次猜测！
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # GOOD：使用慢速密码散列 function
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    password_hash = ph.hash(password)

**❌ 将 MAC 与 ==:** 进行比较

.. code-block:: python

    # BAD：定时攻击揭示了正确的 MAC 的信息！
    if received_mac == computed_mac:  # VULNERABLE
        process_message()

    # GOOD：Constant-时间比较
    import hmac
    if hmac.compare_digest(received_mac, computed_mac):
        process_message()

**❌ 硬编码 keys/秘密：**

.. code-block:: python

    # BAD：源代码中的Keys最终进入版本控制！
    SECRET_KEY = "super_secret_key_12345"
    API_KEY = "ak_live_xxxxxxxxxxxxx"

    # GOOD：使用环境variables或秘密管理
    import os
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # 或者使用：AWS Secrets Manager、HashiCorp Vault 等。

安全检查表（Security Checklist）
--------------------------------------------------

在应用程序中实现加密时请使用此清单。

**开始之前：**

.. code-block:: text

    □ Do I really need custom crypto? (Consider existing solutions first)
    □ Am I using a well-maintained library? (cryptography, not PyCrypto)
    □ Have I read the library's security documentation?

**密钥管理：**

.. code-block:: text

    □ Keys generated with cryptographically secure random (secrets/os.urandom)
    □ Keys are appropriate size (AES-256, RSA ≥3072-bit)
    □ Keys stored securely (not in source code, use env vars or secret manager)
    □ Key rotation plan in place
    □ Different keys for different purposes (encryption vs signing)
    □ Keys protected at rest (encrypted with master key or HSM)

**加密：**

.. code-block:: text

    □ Using authenticated encryption (AES-GCM or ChaCha20-Poly1305)
    □ Nonces are unique per encryption (random 12 bytes for AES-GCM)
    □ Not reusing key+nonce combinations
    □ Associated data (AAD) used where appropriate
    □ Ciphertext includes nonce for decryption
    □ Using RSA-OAEP (not PKCS#1 v1.5) for asymmetric encryption

**签名：**

.. code-block:: text

    □ Using Ed25519 or RSA-PSS (not PKCS#1 v1.5)
    □ Signing the right data (include all relevant fields)
    □ Verifying signatures before trusting data
    □ Handling verification failures securely

**密码存储：**

.. code-block:: text

    □ Using Argon2id, scrypt, or PBKDF2 (not plain hashes)
    □ Unique salt per password (≥16 bytes)
    □ Sufficient iterations/memory cost (tune for ~100ms-500ms)
    □ Rehashing when parameters change
    □ Not logging passwords or hashes

**TLS/网络：**

.. code-block:: text

    □ TLS 1.2 or 1.3 only (no SSL, TLS 1.0, TLS 1.1)
    □ Certificate validation enabled
    □ Using trusted CA certificates
    □ Hostname verification enabled
    □ Certificate pinning for high-security apps

**通用：**

.. code-block:: text

    □ No sensitive data in logs
    □ Secure memory handling (clear keys after use where possible)
    □ Error messages don't leak sensitive information
    □ Timing-safe comparisons for secrets
    □ Dependencies up to date (check for CVEs)

安全随机生成（Secure Random Generation）
----------------------------------------------------------------

密码操作需要不可预测的随机数。 Python 的 ``secrets`` module (Python 3.6+) 提供加密安全随机生成，适用于令牌、密码和 keys。切勿将 ``random`` module 用于安全敏感应用 - 它使用可预测的 PRNG (Mersenne Twister)，可以根据观察到的输出进行逆向工程。

.. code-block:: python

    import secrets
    import os

    # 生成随机 bytes（对于 keys、IV、盐）
    key = secrets.token_bytes(32)      # 256-bit key
    iv = secrets.token_bytes(16)       # 128-bit IV

    # 生成 URL 安全令牌（对于会话 ID，API keys）
    token = secrets.token_urlsafe(32)  # ~43 个字符

    # 生成十六进制令牌
    hex_token = secrets.token_hex(16)  # 32 个十六进制字符

    # 安全随机 integer
    n = secrets.randbelow(100)         # 0 <= n < 100

    # 从序列中安全选择
    password_char = secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789')

    # 替代方案：os.urandom（适用于所有 Python 版本）
    key = os.urandom(32)

加密散列（Cryptographic Hashing）
------------------------------------------------------

Hash functions 从任意数据生成固定大小的摘要。使用 SHA-256 或 SHA-3 进行一般散列。对于密码存储，请使用专用密码散列 functions（请参阅 Key 推导部分）。 Hash functions 是单向的：您无法从 hash 恢复原始数据。它们用于数据完整性验证、数字签名以及作为其他加密操作的构建块。

.. code-block:: python

    import hashlib

    data = b"Hello, World!"

    # SHA-256（推荐一般用途）
    digest = hashlib.sha256(data).hexdigest()
    print(f"SHA-256: {digest}")

    # SHA-3（较新，内部结构不同）
    digest = hashlib.sha3_256(data).hexdigest()
    print(f"SHA3-256: {digest}")

    # BLAKE2（快速、安全、支持密钥）
    digest = hashlib.blake2b(data, digest_size=32).hexdigest()
    print(f"BLAKE2b: {digest}")

    # 带键 BLAKE2（MAC 无单独的 HMAC 结构）
    key = b"secret-key-here!"
    mac = hashlib.blake2b(data, key=key, digest_size=32).hexdigest()

    # 增量哈希（针对大文件）
    h = hashlib.sha256()
    with open("largefile.bin", "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    print(f"File hash: {h.hexdigest()}")

HMAC（基于哈希的消息验证码）（HMAC (Hash-based Message Authentication Code)）
------------------------------------------------------------------------------------------------------------------------------

HMAC 提供消息认证——验证完整性和真实性。与普通的 hashes 不同，HMAC 需要秘密 key，因此只有拥有 key 的各方才能创建或验证 MAC。当您需要确保数据未被篡改并且来自知道秘密的人时，请使用 HMAC。验证 MAC 时，始终使用 constant 时间比较来防止定时攻击。

.. code-block:: python

    import hmac
    import hashlib
    import secrets

    key = secrets.token_bytes(32)
    message = b"Important message"

    # 创建HMAC
    mac = hmac.new(key, message, hashlib.sha256).digest()

    # 验证HMAC（constant-时间比较）
    received_mac = mac  # 实际上，从发件人处收到
    if hmac.compare_digest(mac, received_mac):
        print("Message is authentic")
    else:
        print("Message was tampered with!")

    # HMAC 带十六进制摘要
    mac_hex = hmac.new(key, message, hashlib.sha256).hexdigest()

密钥派生函数（Key Derivation Functions）
----------------------------------------------------------------

Key 推导 functions (KDF) 从密码或其他 key 材料中推导加密 keys。对于密码，请使用可抵抗暴力攻击的慢速 KDF（PBKDF2、Argon2、scrypt）。要从主 key 派生多个 keys，请使用 HKDF。切勿使用普通 hashes (SHA-256) 进行密码存储 - 它们速度太快，每秒允许数十亿次猜测。

.. code-block:: python

    import os
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

    # PBKDF2 - 广泛支持，使用 >= 600,000 次迭代 (OWASP 2023)
    password = b"user-password"
    salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    key = kdf.derive(password)

    # 要验证密码，请再次推导并比较
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,  # 必须使用相同的盐
        iterations=600_000,
    )
    try:
        kdf.verify(password, key)
        print("Password correct")
    except Exception:
        print("Password incorrect")

    # Scrypt - 内存困难，更好地抵抗 GPU/ASIC 攻击
    kdf = Scrypt(salt=salt, length=32, n=2**17, r=8, p=1)
    key = kdf.derive(password)

    # HKDF - 用于从主 key 派生多个 keys （不适用于密码）
    master_key = os.urandom(32)
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=b"encryption-key",
    )
    derived_key = hkdf.derive(master_key)

对称加密：AES-GCM（Symmetric Encryption: AES-GCM）
--------------------------------------------------------------------------------------

AES-GCM（Galois/Counter Mode）是推荐的对称加密模式。它提供经过身份验证的加密：机密性（数据被加密）和完整性（检测到篡改）。身份验证标签确保密文未被修改。对于具有相同 key 的每个加密，始终使用唯一的随机数（使用一次的数字）——重复使用随机数会完全破坏安全性。

::

    ┌─────────────────────────────────────────────────────────────────┐
    │                     AES-GCM ENCRYPTION                          │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   Plaintext ──┬──► AES-GCM ──► Ciphertext                       │
    │               │       │                                         │
    │   Key ────────┤       ├──► Authentication Tag (16 bytes)        │
    │               │       │                                         │
    │   Nonce ──────┘       └──► Associated Data (AAD) authenticated  │
    │   (12 bytes)                but not encrypted                   │
    │                                                                 │
    │   Security: Nonce MUST be unique per key. Random 12-byte        │
    │   nonce is safe for ~2^32 encryptions per key.                  │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘

.. code-block:: python

    import os
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    # 生成随机256-bit key
    key = AESGCM.generate_key(bit_length=256)

    # 创建密码
    aesgcm = AESGCM(key)

    # 加密
    nonce = os.urandom(12)  # 96-bit 随机数，MUST 每次加密都是唯一的
    plaintext = b"Secret message"
    associated_data = b"header"  # 经过身份验证但未加密（可选）

    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    # 密文包含 16-byte 身份验证标签

    # 解密
    decrypted = aesgcm.decrypt(nonce, ciphertext, associated_data)
    assert decrypted == plaintext

    # 篡改检测 - 修改密文引发 exception
    try:
        tampered = bytearray(ciphertext)
        tampered[0] ^= 1  # 翻盖一bit
        aesgcm.decrypt(nonce, bytes(tampered), associated_data)
    except Exception as e:
        print(f"Tampering detected: {e}")

对称加密：ChaCha20-Poly1305（Symmetric Encryption: ChaCha20-Poly1305）
------------------------------------------------------------------------------------------------------------------------------

ChaCha20-Poly1305 是 AES-GCM 的替代品，在没有 AES 硬件加速（移动设备和较旧的 CPU 上常见）的系统上提供类似的安全性和更好的性能。它被 TLS 1.3、WireGuard 和许多现代协议使用。与 AES-GCM 一样，它提供关联数据的经过身份验证的加密 (AEAD)。

.. code-block:: python

    import os
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

    # 生成 key (256-bit)
    key = ChaCha20Poly1305.generate_key()

    # 创建密码
    chacha = ChaCha20Poly1305(key)

    # 加密
    nonce = os.urandom(12)  # 96-bit 随机数
    plaintext = b"Secret message"
    aad = b"additional authenticated data"

    ciphertext = chacha.encrypt(nonce, plaintext, aad)

    # 解密
    decrypted = chacha.decrypt(nonce, ciphertext, aad)
    assert decrypted == plaintext

高级加密：Fernet（High-Level Encryption: Fernet）
------------------------------------------------------------------------------------

Fernet提供了高级、易于使用的对称加密API。它使用 AES-128-CBC 和 HMAC 进行身份验证，处理 IV 生成，并包括可选的基于 TTL 的过期的时间戳。当您需要简单、安全的加密而不用担心底层细节时，请使用 Fernet。缺点是密文稍大，并且没有相关数据支持。

.. code-block:: python

    from cryptography.fernet import Fernet, InvalidToken
    import time

    # 生成 key（安全存储！）
    key = Fernet.generate_key()
    print(f"Key: {key.decode()}")  # Base64 编码

    # 创建 Fernet instance
    f = Fernet(key)

    # 加密
    plaintext = b"Secret message"
    token = f.encrypt(plaintext)
    print(f"Token: {token.decode()}")

    # 解密
    decrypted = f.decrypt(token)
    assert decrypted == plaintext

    # 使用 TTL 解密（生存时间以秒为单位）
    try:
        # 令牌必须是在过去 60 秒内创建的
        decrypted = f.decrypt(token, ttl=60)
    except InvalidToken:
        print("Token expired or invalid")

    # Key 通过 MultiFernet 进行旋转
    from cryptography.fernet import MultiFernet

    old_key = Fernet.generate_key()
    new_key = Fernet.generate_key()

    # MultiFernet 尝试 keys 进行解密
    # 始终使用第一个 key 进行加密
    multi = MultiFernet([Fernet(new_key), Fernet(old_key)])

    # 可以解密来自 key 的令牌
    old_token = Fernet(old_key).encrypt(b"old data")
    decrypted = multi.decrypt(old_token)  # 作品！

    # 使用新的 key 重新加密
    new_token = multi.rotate(old_token)

RSA 密钥生成（RSA Key Generation）
--------------------------------------------------------

RSA 是一种使用公共/私有 key 对的非对称算法。公开key加密数据或验证签名；私人key解密或签名。现代建议：至少使用 2048-bit keys（为了长期安全而使用 3072 或 4096）、公共指数 65537 和 OAEP padding 进行加密，或使用 PSS 进行签名。对于新系统，请考虑使用 Ed25519（签名）或 X25519（key 交换）。

.. code-block:: python

    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    # 生成 RSA key 对
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,  # 最低 2048，长期 4096
    )
    public_key = private_key.public_key()

    # 序列化私有key（PEM格式）
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
    )

    # 序列化私有key，不加密
    private_pem_unencrypted = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # 序列化公共key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # 保存到文件
    with open("private_key.pem", "wb") as f:
        f.write(private_pem)
    with open("public_key.pem", "wb") as f:
        f.write(public_pem)

    # 从文件加载 keys
    with open("private_key.pem", "rb") as f:
        loaded_private = serialization.load_pem_private_key(
            f.read(),
            password=b"passphrase",
        )

    with open("public_key.pem", "rb") as f:
        loaded_public = serialization.load_pem_public_key(f.read())

RSA 加密 (OAEP)（RSA Encryption (OAEP)）
------------------------------------------------------------------------

RSA 加密应始终使用 OAEP（最佳非对称加密 Padding）。切勿将 PKCS#1 v1.5 padding 用于新应用程序 - 它容易受到 padding 预言机攻击。 RSA 只能加密少量数据（key_size/8 - padding 开销），因此它通常用于加密对称 key，然后加密实际数据（混合加密）。

::

    ┌─────────────────────────────────────────────────────────────────┐
    │                    RSA-OAEP ENCRYPTION                          │
    ├─────────────────────────────────────────────────────────────────┤
    │                                                                 │
    │   Plaintext ──► OAEP Padding ──► RSA ──► Ciphertext             │
    │                      │            │                             │
    │                      │      Public Key                          │
    │                      │                                          │
    │   OAEP uses:                                                    │
    │   - MGF1 (Mask Generation Function)                             │
    │   - Hash algorithm (SHA-256 recommended)                        │
    │   - Optional label                                              │
    │                                                                 │
    │   Max plaintext size: key_bytes - 2*hash_bytes - 2              │
    │   For 4096-bit key with SHA-256: 512 - 64 - 2 = 446 bytes       │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘

.. code-block:: python

    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes

    # 生成keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public_key = private_key.public_key()

    # 使用公共 key 进行加密 (OAEP padding)
    plaintext = b"Secret message for RSA"
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # 使用私有key解密
    decrypted = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    assert decrypted == plaintext

混合加密（Hybrid Encryption）
----------------------------------------------

RSA 有大小限制并且速度慢。混合加密将 RSA 的 key 分布优势与对称加密的速度相结合：生成随机对称 key，使用 AES-GCM 加密数据，然后使用 RSA 加密对称 key。接收者用其 RSA 私有 key 解密对称 key，然后解密数据。

.. code-block:: python

    import os
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    def hybrid_encrypt(public_key, plaintext):
        """Encrypt data using hybrid RSA + AES-GCM."""
        # 生成随机数 AES key 和随机数
        aes_key = AESGCM.generate_key(bit_length=256)
        nonce = os.urandom(12)

        # 使用AES-GCM加密数据
        aesgcm = AESGCM(aes_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # 使用 RSA-OAEP 加密 AES key
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
        """Decrypt data using hybrid RSA + AES-GCM."""
        # 用RSA解密AES key
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # 使用AES-GCM解密数据
        aesgcm = AESGCM(aes_key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    # 用法
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public_key = private_key.public_key()

    message = b"This message can be arbitrarily long!" * 1000
    encrypted_key, nonce, ciphertext = hybrid_encrypt(public_key, message)
    decrypted = hybrid_decrypt(private_key, encrypted_key, nonce, ciphertext)
    assert decrypted == message

数字签名：RSA-PSS（Digital Signatures: RSA-PSS）
----------------------------------------------------------------------------------

数字签名证明真实性和完整性。签名者使用他们的私人key来创建签名；任何拥有公共key的人都可以验证它。使用 PSS（概率签名方案）padding 进行 RSA 签名 - 与 PKCS#1 v1.5 不同，它是可证明安全的。对于新应用，请考虑 Ed25519 而不是 RSA。

.. code-block:: python

    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes

    # 生成keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public_key = private_key.public_key()

    message = b"Message to sign"

    # 使用私人key（PSS padding）签名
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    # 与公众验证key
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        print("Signature valid")
    except Exception:
        print("Signature invalid!")

数字签名：Ed25519（Digital Signatures: Ed25519）
----------------------------------------------------------------------------------

Ed25519是一种基于椭圆曲线的现代签名算法。它通过小型 keys (32 bytes) 和签名 (64 bytes) 提供出色的安全性、快速操作并抵御许多实施陷阱。对于新应用程序，除非需要与旧系统兼容，否则优先选择 Ed25519 而不是 RSA。

.. code-block:: python

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization

    # 生成 key 对
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # 签名留言
    message = b"Message to sign"
    signature = private_key.sign(message)

    # 验证签名
    try:
        public_key.verify(signature, message)
        print("Signature valid")
    except Exception:
        print("Signature invalid!")

    # 序列号 keys
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # 公共 key 的 OpenSSH 格式
    public_ssh = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    print(public_ssh.decode())  # ssh-ed25519 AAAA...

椭圆曲线 Diffie-Hellman (ECDH)（Elliptic Curve Diffie-Hellman (ECDH)）
--------------------------------------------------------------------------------------------------------------------------------

ECDH 允许两方通过不安全的通道建立共享秘密。每一方生成一个 key 对，交换公共 keys，并派生相同的共享秘密。将 X25519 (Curve25519) 用于现代应用程序 — 它快速、安全且能够抵抗定时攻击。共享秘密在用作加密 key 之前应通过 KDF 传递。

.. code-block:: python

    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes

    # Alice 生成她的 key 对
    alice_private = X25519PrivateKey.generate()
    alice_public = alice_private.public_key()

    # Bob 生成他的 key 对
    bob_private = X25519PrivateKey.generate()
    bob_public = bob_private.public_key()

    # 交换公共keys（通过不安全通道）
    # Alice 计算共享秘密
    alice_shared = alice_private.exchange(bob_public)

    # Bob 计算共享秘密
    bob_shared = bob_private.exchange(alice_public)

    # 两者都得出相同的共享秘密
    assert alice_shared == bob_shared

    # 使用 HKDF 从共享密钥导出加密 key
    def derive_key(shared_secret, info):
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=info,
        )
        return hkdf.derive(shared_secret)

    encryption_key = derive_key(alice_shared, b"encryption")
    mac_key = derive_key(alice_shared, b"authentication")

使用 Argon2 进行密码哈希处理（Password Hashing with Argon2）
------------------------------------------------------------------------------------------------

Argon2 是密码哈希竞赛（2015 年）的获胜者，也是密码存储的推荐算法。它是内存困难的，使得 GPU/ASIC 攻击成本高昂。将 ``argon2-cffi`` library 用于 Python。将完整的 hash string（包括盐和 parameters）存储在数据库中。

.. code-block:: python

    # pip install argon2-cffi
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError

    ph = PasswordHasher(
        time_cost=3,        # 迭代次数
        memory_cost=65536,  # 内存使用情况（以 KiB 为单位）(64 MB)
        parallelism=4,      # 并联数量 threads
    )

    # Hash 密码（用于存储）
    password = "user-password"
    hash_str = ph.hash(password)
    print(f"Hash: {hash_str}")
    # $argon2id$v=19$m=65536,t=3,p=4$...

    # 验证密码（登录期间）
    try:
        ph.verify(hash_str, password)
        print("Password correct")

        # 检查是否需要重新哈希（parameters 已更改）
        if ph.check_needs_rehash(hash_str):
            new_hash = ph.hash(password)
            # 更新存储的hash
    except VerifyMismatchError:
        print("Password incorrect")
