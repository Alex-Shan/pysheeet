"""Tests for file I/O operations."""

import csv
import gzip
import json
import tempfile
import zipfile
from pathlib import Path


def test_read_write_text(tmp_path):
    """Read and write text files."""
    p = tmp_path / "test.txt"
    content = "Hello, World!\nLine 2"

    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

    with open(p, encoding="utf-8") as f:
        result = f.read()

    assert result == content


def test_read_lines(tmp_path):
    """Read file line by line."""
    p = tmp_path / "lines.txt"
    p.write_text("line1\nline2\nline3\n")

    lines = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            lines.append(line.rstrip())

    assert lines == ["line1", "line2", "line3"]


def test_write_modes(tmp_path):
    """Test different write modes."""
    p = tmp_path / "modes.txt"

    # 写入模式
    with open(p, "w", encoding="utf-8") as f:
        f.write("first")

    # 追加模式
    with open(p, "a", encoding="utf-8") as f:
        f.write(" second")

    assert p.read_text() == "first second"


def test_binary_files(tmp_path):
    """Read and write binary files."""
    p = tmp_path / "binary.bin"
    data = b"\x00\x01\x02\xff"

    with open(p, "wb") as f:
        f.write(data)

    with open(p, "rb") as f:
        result = f.read()

    assert result == data


def test_pathlib_properties(tmp_path):
    """Test pathlib path properties."""
    p = tmp_path / "folder" / "report.pdf"

    assert p.name == "report.pdf"
    assert p.stem == "report"
    assert p.suffix == ".pdf"
    assert p.parent == tmp_path / "folder"


def test_pathlib_with_suffix():
    """Change path suffix."""
    p = Path("/home/user/doc.txt")
    new_p = p.with_suffix(".md")
    assert new_p.suffix == ".md"
    assert new_p.stem == "doc"


def test_pathlib_read_write(tmp_path):
    """Read and write with pathlib."""
    p = tmp_path / "pathlib.txt"

    p.write_text("pathlib content", encoding="utf-8")
    content = p.read_text(encoding="utf-8")

    assert content == "pathlib content"


def test_pathlib_bytes(tmp_path):
    """Read and write bytes with pathlib."""
    p = tmp_path / "bytes.bin"
    data = b"binary data"

    p.write_bytes(data)
    result = p.read_bytes()

    assert result == data


def test_list_directory(tmp_path):
    """List directory contents."""
    (tmp_path / "file1.txt").touch()
    (tmp_path / "file2.txt").touch()
    (tmp_path / "subdir").mkdir()

    items = list(tmp_path.iterdir())
    assert len(items) == 3

    files = [i for i in items if i.is_file()]
    dirs = [i for i in items if i.is_dir()]
    assert len(files) == 2
    assert len(dirs) == 1


def test_glob_pattern(tmp_path):
    """Find files with glob patterns."""
    (tmp_path / "a.py").touch()
    (tmp_path / "b.py").touch()
    (tmp_path / "c.txt").touch()

    py_files = list(tmp_path.glob("*.py"))
    assert len(py_files) == 2


def test_recursive_glob(tmp_path):
    """Recursive glob pattern."""
    (tmp_path / "a.py").touch()
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "b.py").touch()

    py_files = list(tmp_path.rglob("*.py"))
    assert len(py_files) == 2


def test_mkdir_parents(tmp_path):
    """Create nested directories."""
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True, exist_ok=True)

    assert nested.exists()
    assert nested.is_dir()


def test_path_exists(tmp_path):
    """Check path existence and type."""
    file_path = tmp_path / "file.txt"
    file_path.touch()

    dir_path = tmp_path / "dir"
    dir_path.mkdir()

    assert file_path.exists()
    assert file_path.is_file()
    assert not file_path.is_dir()

    assert dir_path.exists()
    assert dir_path.is_dir()
    assert not dir_path.is_file()


def test_temporary_file():
    """Create temporary file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=True
    ) as f:
        f.write("temp content")
        f.flush()
        assert Path(f.name).exists()
        assert f.name.endswith(".txt")


def test_temporary_directory():
    """Create temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        assert p.exists()
        (p / "file.txt").write_text("content")
        assert (p / "file.txt").exists()
    # 目录应在上下文之后删除
    assert not p.exists()


def test_csv_read_write(tmp_path):
    """Read and write CSV files."""
    csv_path = tmp_path / "data.csv"

    # 写
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "age"])
        writer.writerow(["Alice", 30])
        writer.writerow(["Bob", 25])

    # 读
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    assert rows[0] == ["name", "age"]
    assert rows[1] == ["Alice", "30"]


def test_csv_dictreader(tmp_path):
    """Read CSV with DictReader."""
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("name,age\nAlice,30\nBob,25")

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows[0]["name"] == "Alice"
    assert rows[0]["age"] == "30"


def test_json_read_write(tmp_path):
    """Read and write JSON files."""
    json_path = tmp_path / "data.json"
    data = {"name": "Alice", "scores": [95, 87, 92]}

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    with open(json_path, encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded == data


def test_gzip_read_write(tmp_path):
    """Read and write gzip files."""
    gz_path = tmp_path / "file.txt.gz"
    content = "compressed content"

    with gzip.open(gz_path, "wt", encoding="utf-8") as f:
        f.write(content)

    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        result = f.read()

    assert result == content


def test_zipfile_create_extract(tmp_path):
    """Create and extract zip archives."""
    zip_path = tmp_path / "archive.zip"
    file1 = tmp_path / "file1.txt"
    file1.write_text("content 1")

    # 创建邮编
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(file1, "file1.txt")
        zf.writestr("file2.txt", "content 2")

    # List 内容
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert "file1.txt" in names
        assert "file2.txt" in names

    # 提炼
    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    assert (extract_dir / "file1.txt").read_text() == "content 1"
    assert (extract_dir / "file2.txt").read_text() == "content 2"


def test_symlink(tmp_path):
    """Create and read symbolic links."""
    target = tmp_path / "target.txt"
    target.write_text("target content")

    link = tmp_path / "link.txt"
    link.symlink_to(target)

    assert link.is_symlink()
    assert link.read_text() == "target content"
    assert link.resolve() == target.resolve()


def test_file_stat(tmp_path):
    """Get file statistics."""
    p = tmp_path / "file.txt"
    p.write_text("some content")

    stat = p.stat()
    assert stat.st_size == len("some content")
    assert stat.st_mtime > 0


def test_shutil_copy(tmp_path):
    """Copy files with shutil."""
    import shutil

    src = tmp_path / "source.txt"
    src.write_text("content")

    # 复制 - 仅内容
    dst1 = tmp_path / "dest1.txt"
    shutil.copy(src, dst1)
    assert dst1.read_text() == "content"

    # copy2 - 保留元数据
    dst2 = tmp_path / "dest2.txt"
    shutil.copy2(src, dst2)
    assert dst2.read_text() == "content"

    # 复制到目录
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    shutil.copy(src, subdir)
    assert (subdir / "source.txt").exists()


def test_shutil_copytree(tmp_path):
    """Copy directory tree with shutil."""
    import shutil

    # 创建源结构
    src = tmp_path / "source"
    src.mkdir()
    (src / "file1.txt").write_text("content1")
    (src / "sub").mkdir()
    (src / "sub" / "file2.txt").write_text("content2")

    # 复制树
    dst = tmp_path / "dest"
    shutil.copytree(src, dst)

    assert (dst / "file1.txt").read_text() == "content1"
    assert (dst / "sub" / "file2.txt").read_text() == "content2"


def test_shutil_copytree_ignore(tmp_path):
    """Copy directory tree with ignore patterns."""
    import shutil

    src = tmp_path / "source"
    src.mkdir()
    (src / "keep.txt").write_text("keep")
    (src / "ignore.pyc").write_text("ignore")

    dst = tmp_path / "dest"
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.pyc"))

    assert (dst / "keep.txt").exists()
    assert not (dst / "ignore.pyc").exists()


def test_shutil_copytree_dirs_exist_ok(tmp_path):
    """Copy into existing directory."""
    import shutil

    src = tmp_path / "source"
    src.mkdir()
    (src / "new.txt").write_text("new")

    dst = tmp_path / "dest"
    dst.mkdir()
    (dst / "existing.txt").write_text("existing")

    shutil.copytree(src, dst, dirs_exist_ok=True)

    assert (dst / "new.txt").exists()
    assert (dst / "existing.txt").exists()


def test_shutil_move(tmp_path):
    """Move files and directories with shutil."""
    import shutil

    # 移动文件
    src = tmp_path / "source.txt"
    src.write_text("content")
    dst = tmp_path / "dest.txt"
    shutil.move(src, dst)

    assert not src.exists()
    assert dst.read_text() == "content"

    # 移至目录
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    shutil.move(dst, subdir)
    assert (subdir / "dest.txt").exists()


def test_shutil_rmtree(tmp_path):
    """Remove directory tree with shutil."""
    import shutil

    d = tmp_path / "to_delete"
    d.mkdir()
    (d / "file.txt").write_text("content")
    (d / "sub").mkdir()
    (d / "sub" / "nested.txt").write_text("nested")

    shutil.rmtree(d)
    assert not d.exists()


def test_shutil_disk_usage(tmp_path):
    """Get disk usage statistics."""
    import shutil

    usage = shutil.disk_usage(tmp_path)
    assert usage.total > 0
    assert usage.free > 0
    assert usage.used >= 0


def test_shutil_which():
    """Find executable in PATH."""
    import shutil

    python = shutil.which("python")
    assert python is not None

    nonexistent = shutil.which("nonexistent_command_xyz")
    assert nonexistent is None


def test_shutil_make_archive(tmp_path):
    """Create archives with shutil."""
    import shutil

    # 创建源
    src = tmp_path / "source"
    src.mkdir()
    (src / "file.txt").write_text("content")

    # 创建 zip 存档
    archive = shutil.make_archive(str(tmp_path / "backup"), "zip", src)
    assert Path(archive).exists()
    assert archive.endswith(".zip")


def test_shutil_unpack_archive(tmp_path):
    """Extract archives with shutil."""
    import shutil

    # 创建并打包
    src = tmp_path / "source"
    src.mkdir()
    (src / "file.txt").write_text("content")
    archive = shutil.make_archive(str(tmp_path / "backup"), "zip", src)

    # 打开包装
    extract = tmp_path / "extracted"
    shutil.unpack_archive(archive, extract)
    assert (extract / "file.txt").read_text() == "content"
