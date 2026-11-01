"""
Tests for operating system operations.

These tests demonstrate Python's os module for file system operations,
process management, environment variables, and path manipulation.
"""

import os
import platform
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestSystemInfo:
    """Test system information functions."""

    def test_os_name(self):
        """Test os.name returns valid value."""
        assert os.name in ("posix", "nt")

    def test_platform_system(self):
        """Test platform.system returns valid value."""
        assert platform.system() in ("Linux", "Darwin", "Windows")

    def test_cpu_count(self):
        """Test cpu_count returns positive integer."""
        count = os.cpu_count()
        assert count is not None
        assert count > 0

    def test_getpid(self):
        """Test getpid returns positive integer."""
        pid = os.getpid()
        assert pid > 0

    def test_getcwd(self):
        """Test getcwd returns valid path."""
        cwd = os.getcwd()
        assert os.path.isdir(cwd)


class TestEnvironmentVariables:
    """Test environment variable operations."""

    def test_get_env(self):
        """Test getting environment variable."""
        # PATH 应该存在于所有系统上
        path = os.environ.get("PATH")
        assert path is not None

    def test_getenv_default(self):
        """Test getenv with default value."""
        value = os.getenv("NONEXISTENT_VAR_12345", "default")
        assert value == "default"

    def test_set_env(self):
        """Test setting environment variable."""
        os.environ["TEST_VAR_PYSHEEET"] = "test_value"
        assert os.environ["TEST_VAR_PYSHEEET"] == "test_value"
        del os.environ["TEST_VAR_PYSHEEET"]

    def test_env_not_found(self):
        """Test KeyError for missing env var."""
        with pytest.raises(KeyError):
            _ = os.environ["NONEXISTENT_VAR_12345"]


class TestPathOperations:
    """Test path manipulation functions."""

    def test_join(self):
        """Test os.path.join."""
        path = os.path.join("dir1", "dir2", "file.txt")
        assert "dir1" in path
        assert "dir2" in path
        assert "file.txt" in path

    def test_dirname_basename(self):
        """Test dirname and basename."""
        path = os.path.join("home", "user", "file.txt")
        assert os.path.basename(path) == "file.txt"
        assert "user" in os.path.dirname(path)

    def test_splitext(self):
        """Test splitext."""
        name, ext = os.path.splitext("file.txt")
        assert name == "file"
        assert ext == ".txt"

    def test_abspath(self):
        """Test abspath returns absolute path."""
        abs_path = os.path.abspath(".")
        assert os.path.isabs(abs_path)

    def test_exists(self):
        """Test path existence checks."""
        assert os.path.exists(".")
        assert not os.path.exists("/nonexistent/path/12345")

    def test_isfile_isdir(self):
        """Test isfile and isdir."""
        assert os.path.isdir(".")
        # 创建临时文件来测试 isfile
        with tempfile.NamedTemporaryFile() as f:
            assert os.path.isfile(f.name)


class TestDirectoryOperations:
    """Test directory operations."""

    def test_mkdir_rmdir(self):
        """Test creating and removing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "test_dir")
            os.mkdir(new_dir)
            assert os.path.isdir(new_dir)
            os.rmdir(new_dir)
            assert not os.path.exists(new_dir)

    def test_makedirs(self):
        """Test creating nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "a", "b", "c")
            os.makedirs(nested)
            assert os.path.isdir(nested)

    def test_makedirs_exist_ok(self):
        """Test makedirs with exist_ok."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(tmpdir, exist_ok=True)  # 不应该提高

    def test_listdir(self):
        """Test listing directory contents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建一些文件
            Path(tmpdir, "file1.txt").touch()
            Path(tmpdir, "file2.txt").touch()
            entries = os.listdir(tmpdir)
            assert "file1.txt" in entries
            assert "file2.txt" in entries

    def test_walk(self):
        """Test walking directory tree."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建嵌套结构
            os.makedirs(os.path.join(tmpdir, "subdir"))
            Path(tmpdir, "file1.txt").touch()
            Path(tmpdir, "subdir", "file2.txt").touch()

            files_found = []
            for root, dirs, files in os.walk(tmpdir):
                for f in files:
                    files_found.append(f)

            assert "file1.txt" in files_found
            assert "file2.txt" in files_found


class TestFileOperations:
    """Test file operations."""

    def test_rename(self):
        """Test renaming file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old = os.path.join(tmpdir, "old.txt")
            new = os.path.join(tmpdir, "new.txt")
            Path(old).write_text("content")
            os.rename(old, new)
            assert not os.path.exists(old)
            assert os.path.exists(new)

    def test_remove(self):
        """Test removing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "file.txt")
            Path(path).write_text("content")
            os.remove(path)
            assert not os.path.exists(path)

    def test_getsize(self):
        """Test getting file size."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("hello")
            path = f.name
        try:
            size = os.path.getsize(path)
            assert size == 5
        finally:
            os.unlink(path)


class TestSubprocess:
    """Test subprocess operations."""

    def test_run_simple(self):
        """Test simple subprocess.run."""
        result = subprocess.run(
            ["echo", "hello"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "hello" in result.stdout

    def test_check_output(self):
        """Test subprocess.check_output."""
        output = subprocess.check_output(["echo", "test"], text=True)
        assert "test" in output

    def test_run_with_input(self):
        """Test subprocess with input."""
        result = subprocess.run(
            ["cat"], input="hello world", capture_output=True, text=True
        )
        assert result.stdout == "hello world"


class TestTempFiles:
    """Test temporary file operations."""

    def test_named_temp_file(self):
        """Test NamedTemporaryFile."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as f:
            f.write("test data")
            f.flush()
            assert os.path.exists(f.name)
            assert f.name.endswith(".txt")

    def test_temp_directory(self):
        """Test TemporaryDirectory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assert os.path.isdir(tmpdir)
            # 里面创建文件
            path = os.path.join(tmpdir, "test.txt")
            Path(path).write_text("data")
            assert os.path.exists(path)
        # 目录应该被删除
        assert not os.path.exists(tmpdir)

    def test_gettempdir(self):
        """Test getting temp directory path."""
        tmpdir = tempfile.gettempdir()
        assert os.path.isdir(tmpdir)


class TestPathlib:
    """Test pathlib operations."""

    def test_path_creation(self):
        """Test creating Path objects."""
        p = Path("/home/user/file.txt")
        assert p.name == "file.txt"
        assert p.stem == "file"
        assert p.suffix == ".txt"

    def test_path_join(self):
        """Test joining paths with /."""
        p = Path("/home") / "user" / "file.txt"
        assert str(p) == "/home/user/file.txt"

    def test_path_parent(self):
        """Test getting parent."""
        p = Path("/home/user/file.txt")
        assert p.parent == Path("/home/user")

    def test_path_exists(self):
        """Test path existence."""
        assert Path(".").exists()
        assert Path(".").is_dir()

    def test_read_write_text(self):
        """Test reading and writing text."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "test.txt"
            p.write_text("hello world")
            assert p.read_text() == "hello world"

    def test_mkdir(self):
        """Test creating directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "a" / "b" / "c"
            p.mkdir(parents=True)
            assert p.is_dir()

    def test_glob(self):
        """Test glob pattern matching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file1.py").touch()
            (Path(tmpdir) / "file2.py").touch()
            (Path(tmpdir) / "file3.txt").touch()

            py_files = list(Path(tmpdir).glob("*.py"))
            assert len(py_files) == 2

    def test_iterdir(self):
        """Test iterating directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file1.txt").touch()
            (Path(tmpdir) / "file2.txt").touch()

            entries = list(Path(tmpdir).iterdir())
            assert len(entries) == 2


class TestPsutil:
    """Test psutil operations."""

    @pytest.fixture
    def psutil_available(self):
        """Check if psutil is installed."""
        try:
            import psutil

            return psutil
        except ImportError:
            pytest.skip("psutil not installed")

    def test_cpu_count(self, psutil_available):
        """Test CPU count."""
        psutil = psutil_available
        logical = psutil.cpu_count()
        physical = psutil.cpu_count(logical=False)
        assert logical > 0
        assert physical > 0
        assert logical >= physical

    def test_cpu_percent(self, psutil_available):
        """Test CPU percentage."""
        psutil = psutil_available
        percent = psutil.cpu_percent(interval=0.1)
        assert 0 <= percent <= 100

    def test_virtual_memory(self, psutil_available):
        """Test virtual memory info."""
        psutil = psutil_available
        mem = psutil.virtual_memory()
        assert mem.total > 0
        assert mem.available > 0
        assert 0 <= mem.percent <= 100

    def test_disk_usage(self, psutil_available):
        """Test disk usage."""
        psutil = psutil_available
        usage = psutil.disk_usage("/")
        assert usage.total > 0
        assert usage.used >= 0
        assert 0 <= usage.percent <= 100

    def test_process(self, psutil_available):
        """Test current process info."""
        psutil = psutil_available
        p = psutil.Process()
        assert p.pid == os.getpid()
        assert p.name()
        assert p.num_threads() > 0

    def test_boot_time(self, psutil_available):
        """Test boot time."""
        psutil = psutil_available
        boot = psutil.boot_time()
        assert boot > 0
