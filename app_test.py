"""Test app.py."""

import multiprocessing
import platform
import unittest
import requests
import os

from pathlib import Path
from werkzeug.exceptions import NotFound
from flask_testing import LiveServerTestCase

from app import acme, find_key, static_proxy, index_redirection, page_not_found
from app import redirect_legacy_rtd_paths
from app import redirect_legacy_flat_paths, redirect_canonical_host
from app import _resolve_legacy_flat_target

from app import ROOT
from app import app

if platform.system() == "Darwin":
    multiprocessing.set_start_method("fork")


class PysheeetTest(LiveServerTestCase):
    """Test app."""

    def create_app(self):
        """Create a app for test."""
        # 删除环境 ACME_TOKEN*
        for k, v in os.environ.items():
            if not k.startswith("ACME_TOKEN"):
                continue
            del os.environ[k]

        self.token = "token"
        self.key = "key"
        os.environ["ACME_TOKEN"] = self.token
        os.environ["ACME_KEY"] = self.key
        os.environ["FLASK_ENV"] = "development"
        os.environ["FLASK_DEBUG"] = "1"
        app.config["TESTING"] = True
        app.config["LIVESERVER_PORT"] = 0
        return app

    def check_security_headers(self, resp):
        """Check security headers."""
        headers = resp.headers
        self.assertTrue("Content-Security-Policy" in headers)
        self.assertTrue("X-Content-Type-Options" in headers)
        self.assertTrue("Content-Security-Policy" in headers)
        self.assertTrue("Feature-Policy" in headers)
        self.assertEqual(headers["Feature-Policy"], "geolocation 'none'")
        self.assertEqual(headers["X-Frame-Options"], "SAMEORIGIN")

    def check_csrf_cookies(self, resp):
        """Check cookies for csrf."""
        cookies = resp.cookies
        self.assertTrue(cookies.get("__Secure-session"))
        self.assertTrue(cookies.get("__Secure-csrf-token"))

    def test_index_redirection_req(self):
        """Test that send a request for the index page."""
        url = self.get_server_url()
        resp = requests.get(url)
        self.check_security_headers(resp)
        self.check_csrf_cookies(resp)
        self.assertEqual(resp.status_code, 200)

    def test_static_proxy_req(self):
        """Test that send a request for notes."""
        url = self.get_server_url()
        notes = Path(ROOT) / "notes"
        for html in notes.rglob("*.html"):
            page = html.relative_to(ROOT)
            u = f"{url}/{page}"
            resp = requests.get(u)
            self.check_security_headers(resp)
            self.check_csrf_cookies(resp)
            self.assertEqual(resp.status_code, 200)

    def test_acme_req(self):
        """Test that send a request for a acme key."""
        url = self.get_server_url()
        u = url + "/.well-known/acme-challenge/token"
        resp = requests.get(u)
        self.check_security_headers(resp)
        self.assertEqual(resp.status_code, 200)

        u = url + "/.well-known/acme-challenge/foo"
        resp = requests.get(u)
        self.check_security_headers(resp)
        self.assertEqual(resp.status_code, 404)

    def test_find_key(self):
        """Test that find a acme key from the environment."""
        token = self.token
        key = self.key
        self.assertEqual(find_key(token), key)

        del os.environ["ACME_TOKEN"]
        del os.environ["ACME_KEY"]

        os.environ["ACME_TOKEN_ENV"] = token
        os.environ["ACME_KEY_ENV"] = key
        self.assertEqual(find_key(token), key)

        del os.environ["ACME_TOKEN_ENV"]
        del os.environ["ACME_KEY_ENV"]

    def test_acme(self):
        """Test that send a request for a acme key."""
        token = self.token
        key = self.key
        self.assertEqual(acme(token), key)

        token = token + "_env"
        key = key + "_env"
        os.environ["ACME_TOKEN_ENV"] = token
        os.environ["ACME_KEY_ENV"] = key
        self.assertEqual(find_key(token), key)

        del os.environ["ACME_TOKEN_ENV"]
        del os.environ["ACME_KEY_ENV"]

        self.assertRaises(NotFound, acme, token)

    def test_index_redirection(self):
        """Test index page redirection."""
        resp = index_redirection()
        self.assertEqual(resp.status_code, 200)
        resp.close()

    def test_static_proxy(self):
        """Test that request static pages."""
        notes = Path(ROOT) / "notes"
        for html in notes.rglob("*.html"):
            u = html.relative_to(ROOT)
            resp = static_proxy(u)
            self.assertEqual(resp.status_code, 200)
            resp.close()

        u = "notes/../conf.py"
        _, code = static_proxy(u)
        self.assertEqual(code, 404)

    def test_page_not_found(self):
        """Test page not found."""
        html, status_code = page_not_found(None)
        self.assertEqual(status_code, 404)

    def test_legacy_rtd_path_redirect(self):
        """Legacy /en/<slug>/... must 301 to the flat canonical URL."""
        url = self.get_server_url()
        cases = {
            "/en/latest/notes/basic/python-basic.html": (
                "/notes/basic/python-basic.html"
            ),
            "/en/stable/index.html": "/index.html",
            "/en/0.1.0/notes/asyncio/index.html": (
                "/notes/asyncio/index.html"
            ),
        }
        for legacy, flat in cases.items():
            resp = requests.get(url + legacy, allow_redirects=False)
            self.assertEqual(resp.status_code, 301)
            self.assertTrue(resp.headers["Location"].endswith(flat))

    def test_redirect_legacy_rtd_paths_passthrough(self):
        """Non-legacy paths must not be intercepted."""
        with app.test_request_context("/notes/basic/python-basic.html"):
            self.assertIsNone(redirect_legacy_rtd_paths())

    def test_redirect_legacy_rtd_paths_match(self):
        """Legacy /en/<slug>/... returns a 301 redirect response."""
        with app.test_request_context("/en/latest/index.html"):
            resp = redirect_legacy_rtd_paths()
            self.assertEqual(resp.status_code, 301)
            self.assertTrue(resp.headers["Location"].endswith("/index.html"))

    def test_resolve_legacy_flat_target_known(self):
        """Known legacy flat paths resolve to their new nested URLs."""
        cases = {
            "notes/python-sqlalchemy.html": (
                "notes/database/python-sqlalchemy.html"
            ),
            "notes/python-typing.html": "notes/basic/python-typing.html",
            "notes/python-socket.html": "notes/network/python-socket.html",
            "appendix/python-walrus.html": (
                "notes/appendix/python-walrus.html"
            ),
            "notes/multitasking/index.html": "notes/concurrency/index.html",
            "notes/pytorch/pytorch.html": "notes/llm/pytorch.html",
            # 中间重组快照 Google 仍已编入索引。
            "notes/container/python-dict.html": (
                "notes/basic/python-dict.html"
            ),
            "notes/iteration/python-generator.html": (
                "notes/basic/python-generator.html"
            ),
            "notes/string/python-unicode.html": (
                "notes/basic/python-unicode.html"
            ),
            "notes/cryptography/python-crypto.html": (
                "notes/security/python-crypto.html"
            ),
            "notes/io/python-socket.html": (
                "notes/network/python-socket.html"
            ),
            "notes/os/python-socket.html": (
                "notes/network/python-socket.html"
            ),
            "notes/security/python-ssh.html": (
                "notes/network/python-ssh.html"
            ),
            "notes/pytorch/slurm.html": "notes/hpc/slurm.html",
            "notes/llm/vllm-serving.html": "notes/llm/llm-serving.html",
            "notes/extension/python-c-extensions.html": (
                "notes/extension/python-cext-modern.html"
            ),
            "notes/appendix/python-asyncio.html": (
                "notes/asyncio/python-asyncio-guide.html"
            ),
            # 没有直接后继的已删除页面将转到根目录。
            "notes/python-aws.html": "index.html",
            "notes/testing/python-tests.html": "index.html",
        }
        for old, new in cases.items():
            self.assertEqual(_resolve_legacy_flat_target(old), new)

    def test_resolve_legacy_flat_target_unknown(self):
        """Unknown paths return None so the request is not redirected."""
        cases = (
            "notes/basic/python-basic.html",
            "notes/totally_made_up.html",
            "about.html",
        )
        for path in cases:
            self.assertIsNone(_resolve_legacy_flat_target(path))

    def test_redirect_legacy_flat_paths_passthrough(self):
        """Current nested URLs are not intercepted by the redirector."""
        with app.test_request_context("/notes/basic/python-basic.html"):
            self.assertIsNone(redirect_legacy_flat_paths())

    def test_redirect_legacy_flat_paths_match(self):
        """A renamed flat URL returns 301 to its new nested location."""
        with app.test_request_context("/notes/python-sqlalchemy.html"):
            resp = redirect_legacy_flat_paths()
            self.assertEqual(resp.status_code, 301)
            self.assertTrue(
                resp.headers["Location"].endswith(
                    "/notes/database/python-sqlalchemy.html"
                )
            )

    def test_redirect_canonical_host_bare(self):
        """Requests to pythonsheets.com 301 to www.pythonsheets.com."""
        with app.test_request_context(
            "/notes/basic/python-basic.html",
            base_url="https://pythonsheets.com",
        ):
            resp = redirect_canonical_host()
            self.assertEqual(resp.status_code, 301)
            self.assertEqual(
                resp.headers["Location"],
                "https://www.pythonsheets.com"
                "/notes/basic/python-basic.html",
            )

    def test_redirect_canonical_host_preserves_query(self):
        """Bare-host redirect preserves the query string."""
        with app.test_request_context(
            "/search?q=typing",
            base_url="https://pythonsheets.com",
        ):
            resp = redirect_canonical_host()
            self.assertEqual(resp.status_code, 301)
            self.assertEqual(
                resp.headers["Location"],
                "https://www.pythonsheets.com/search?q=typing",
            )

    def test_redirect_canonical_host_passthrough(self):
        """Requests already on the canonical www host are not redirected."""
        with app.test_request_context(
            "/",
            base_url="https://www.pythonsheets.com",
        ):
            self.assertIsNone(redirect_canonical_host())


if __name__ == "__main__":
    unittest.main()
