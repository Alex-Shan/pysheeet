.. meta::
    :description lang=zh_CN: Python 安全和密码学指南，涵盖现代加密、TLS/SSL、常见漏洞和安全编码实践
    :keywords: Python, Python3, security, cryptography, encryption, AES, RSA, TLS, SSL, vulnerability, padding oracle, injection, secure coding

========================
安全（Security）
========================

安全性对于保护传输中和 rest 中的数据至关重要。本节介绍使用维护良好的 libraries（如 ``cryptography`` 和 ``argon2-cffi`` ）的现代加密实践，以及常见的安全漏洞以及如何避免它们。我们强调安全默认值：经过身份验证的加密（AES-GCM）、正确的key派生（PBKDF2、Argon2）、安全签名（Ed25519、RSA-PSS）以及正确的TLS配置。

了解漏洞同样重要 - 了解为什么没有身份验证的 AES-CBC 或 PKCS#1 v1.5 padding 等遗留模式是危险的，可以帮助您识别和修复现有系统中的不安全代码。

.. toctree::
    :maxdepth: 1

    python-crypto
    python-tls
    python-vulnerability
