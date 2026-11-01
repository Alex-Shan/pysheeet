.. meta::
    :description lang=zh_CN: Python TLS/SSL 和 X.509 证书指南，涵盖安全 HTTPS 服务器、证书生成、CSR 创建以及使用密码学 library 的证书验证
    :keywords: Python, Python3, TLS, SSL, HTTPS, X.509, Certificate, CSR, Certificate Authority, Self-Signed, SSLContext, cryptography

========================================================================
TLS/SSL及证书（TLS/SSL and Certificates）
========================================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

传输层安全 (TLS) 通过网络提供加密、经过身份验证的通信。本指南涵盖在 Python 中创建安全的 HTTPS 服务器、生成证书以及正确的 TLS 配置。我们使用 ``ssl`` module的 ``SSLContext`` API（不是已弃用的 ``wrap_socket`` ）和 ``cryptography`` library进行证书操作。始终使用 TLS、1.2 或 1.3 — 旧版本存在已知漏洞。

.. warning::

    对于生产，请始终使用来自受信任的证书颁发机构 (CA) 的证书，例如 Let's Encrypt。自签名证书仅用于开发和测试。切勿在生产代码中禁用证书验证。

安全 HTTPS 服务器（Secure HTTPS Server）
------------------------------------------------------------------

使用具有安全默认值的 ``SSLContext`` 创建 HTTPS 服务器。上下文配置TLS版本、密码套件和证书验证。始终加载证书链和私有 key。对于生产，请使用真实 CA 的证书。

.. code-block:: python

    import ssl
    from http.server import HTTPServer, SimpleHTTPRequestHandler

    def create_secure_context(certfile, keyfile):
        """Create SSLContext with secure defaults."""
        # 仅 TLS 1.2+，安全密码
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        # 加载证书和私有key
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)

        # 禁用不安全的选项
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1

        return context

    # 创建服务器
    host, port = "localhost", 8443
    context = create_secure_context("cert.pem", "key.pem")

    httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Serving HTTPS on https://{host}:{port}")
    httpd.serve_forever()

保护 HTTPS 客户端（Secure HTTPS Client）
------------------------------------------------------------------

当发出 HTTPS 请求时，Python 默认验证证书。对于自定义 CA 证书或客户端身份验证，请配置 ``SSLContext`` 。切勿在生产中使用 set ``verify=False`` 或禁用主机名检查。

.. code-block:: python

    import ssl
    import urllib.request

    # 默认安全上下文（验证证书）
    context = ssl.create_default_context()

    # 发出 HTTPS 请求
    url = "https://example.com"
    with urllib.request.urlopen(url, context=context) as response:
        print(response.read().decode())

    # 定制CA证书（e.g.，内部CA）
    context = ssl.create_default_context()
    context.load_verify_locations("internal-ca.pem")

    # 客户端证书身份验证 (mTLS)
    context = ssl.create_default_context()
    context.load_cert_chain(certfile="client.pem", keyfile="client-key.pem")

    # 使用请求library（推荐用于HTTP）
    import requests

    # 默认（安全）
    response = requests.get("https://example.com")

    # 定制CA
    response = requests.get("https://internal.example.com", verify="internal-ca.pem")

    # 客户证书
    response = requests.get(
        "https://secure.example.com",
        cert=("client.pem", "client-key.pem"),
    )

生成自签名证书（Generate Self-Signed Certificate）
----------------------------------------------------------------------------------

自签名证书对于开发和测试很有用。该证书由其自己的私有 key 而不是 CA 签名。浏览器将显示有关自签名证书的警告。使用 ``cryptography`` library 进行证书生成 — 它比调用 OpenSSL 更适合 Pythonic。

.. code-block:: python

    import ipaddress
    from datetime import datetime, timedelta
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    # 生成私有key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )

    # 证书主题和颁发者（自签名相同）
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    # 构建证书
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("*.localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .sign(private_key, hashes.SHA256())
    )

    # 保存私人key
    with open("key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # 保存证书
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("Generated key.pem and cert.pem")

生成证书签名请求 (CSR)（Generate Certificate Signing Request (CSR)）
--------------------------------------------------------------------------------------------------------------------

CSR 被发送到证书颁发机构以获得签名证书。它包含您的公开key和身份信息。 CA 验证您的身份并返回签名证书。确保您的私人 key 保密——切勿将其发送至 CA。

.. code-block:: python

    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    # 生成私有key（保守秘密！）
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )

    # 构建 CSR
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
            x509.NameAttribute(NameOID.COMMON_NAME, "www.example.com"),
        ]))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("www.example.com"),
                x509.DNSName("example.com"),
                x509.DNSName("api.example.com"),
            ]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )

    # 保存私人key
    with open("private.key", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # 保存CSR（发送至CA）
    with open("request.csr", "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))

    print("Generated private.key and request.csr")
    print("Send request.csr to your CA, keep private.key secret!")

读取证书信息（Read Certificate Information）
------------------------------------------------------------------------

解析和检查 X.509 证书以查看主题、颁发者、有效期、扩展名和其他 attributes。对于 debugging 证书问题很有用。

.. code-block:: python

    from cryptography import x509
    from cryptography.hazmat.primitives import serialization

    # 从文件加载证书
    with open("cert.pem", "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read())

    # 基本信息
    print(f"Subject: {cert.subject}")
    print(f"Issuer: {cert.issuer}")
    print(f"Serial: {cert.serial_number}")
    print(f"Not Before: {cert.not_valid_before}")
    print(f"Not After: {cert.not_valid_after}")

    # 获取特定主题 attributes
    cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
    if cn:
        print(f"Common Name: {cn[0].value}")

    # 检查扩展
    try:
        san = cert.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        )
        print(f"SANs: {san.value.get_values_for_type(x509.DNSName)}")
    except x509.ExtensionNotFound:
        print("No SAN extension")

    # 检查是否自签名
    is_self_signed = cert.subject == cert.issuer
    print(f"Self-signed: {is_self_signed}")

    # 验证证书签名（仅限自签名）
    if is_self_signed:
        public_key = cert.public_key()
        try:
            # 这验证了证书是由自己的 key 签名的
            public_key.verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                cert.signature_algorithm_parameters,
            )
            print("Signature valid")
        except Exception as e:
            print(f"Signature invalid: {e}")

创建证书颁发机构（Create a Certificate Authority）
--------------------------------------------------------------------------------

对于内部使用，您可以创建自己的 CA 来签署证书。 CA 证书分发给客户端，然后客户端信任由 CA 签名的任何证书。这对于开发环境或内部服务很有用。

.. code-block:: python

    import ipaddress
    from datetime import datetime, timedelta
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    def create_ca():
        """Create a Certificate Authority."""
        # 生成CA私有key
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )

        # CA 证书（自签名）
        ca_name = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Internal CA"),
            x509.NameAttribute(NameOID.COMMON_NAME, "My Internal Root CA"),
        ])

        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(ca_name)
            .issuer_name(ca_name)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=3650))  # 10年
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=0),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(ca_key, hashes.SHA256())
        )

        return ca_key, ca_cert

    def sign_csr(ca_key, ca_cert, csr_path, days=365):
        """Sign a CSR with the CA."""
        with open(csr_path, "rb") as f:
            csr = x509.load_pem_x509_csr(f.read())

        cert = (
            x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(ca_cert.subject)
            .public_key(csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=days))
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
        )

        # 从 CSR 复制扩展名
        for ext in csr.extensions:
            cert = cert.add_extension(ext.value, ext.critical)

        return cert.sign(ca_key, hashes.SHA256())

    # 创建CA
    ca_key, ca_cert = create_ca()

    # 保存 CA 文件
    with open("ca-key.pem", "wb") as f:
        f.write(ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(b"ca-password"),
        ))

    with open("ca-cert.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    print("Created ca-key.pem (keep secret!) and ca-cert.pem (distribute to clients)")

TLS 版本与加密套件信息（TLS Version and Cipher Information）
--------------------------------------------------------------------------------------------------

检查 TLS 连接详细信息，包括协议版本、密码套件和对等证书。对于 debugging 和安全审核很有用。

.. code-block:: python

    import ssl
    import socket

    def get_tls_info(hostname, port=443):
        """Get TLS connection information for a host."""
        context = ssl.create_default_context()

        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(f"TLS Version: {ssock.version()}")
                print(f"Cipher: {ssock.cipher()}")

                # 同行证书
                cert = ssock.getpeercert()
                print(f"Subject: {dict(x[0] for x in cert['subject'])}")
                print(f"Issuer: {dict(x[0] for x in cert['issuer'])}")
                print(f"Not Before: {cert['notBefore']}")
                print(f"Not After: {cert['notAfter']}")

                # 主题替代名称
                if 'subjectAltName' in cert:
                    sans = [x[1] for x in cert['subjectAltName']]
                    print(f"SANs: {sans}")

    get_tls_info("www.google.com")

证书固定（Certificate Pinning）
--------------------------------------------------

证书固定通过验证服务器的证书与预期的 value 匹配来增加额外的安全层。这可以防止使用欺诈性颁发的证书进行攻击。固定公共 key (SPKI) 而不是证书，以便在证书续订后继续有效。

.. code-block:: python

    import ssl
    import socket
    import hashlib
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization

    def get_certificate_pin(hostname, port=443):
        """Get the SPKI pin for a certificate."""
        context = ssl.create_default_context()

        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # 获取DER格式的证书
                der_cert = ssock.getpeercert(binary_form=True)

        # 解析证书
        cert = x509.load_der_x509_certificate(der_cert)

        # 获取 DER 格式的公共 key (SPKI)
        spki = cert.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # SHA-256 hash SPKI
        pin = hashlib.sha256(spki).digest()
        return pin

    def verify_pin(hostname, expected_pin, port=443):
        """Verify certificate matches expected pin."""
        actual_pin = get_certificate_pin(hostname, port)
        if actual_pin != expected_pin:
            raise ssl.SSLError(f"Certificate pin mismatch for {hostname}")
        print(f"Pin verified for {hostname}")

    # 获取 pin（执行一次，存储结果）
    pin = get_certificate_pin("www.google.com")
    print(f"Pin (base64): {__import__('base64').b64encode(pin).decode()}")

    # 验证后续连接的引脚
    verify_pin("www.google.com", pin)
