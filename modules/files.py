"""
modules/files.py — DOT File Management Module

Safe file and directory operations.
"""

from __future__ import annotations

import datetime
import os
import shutil
from pathlib import Path
from typing import Optional

from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger
from core.permissions import PermissionLevel

log = get_logger("files")


def _safe_path(path_str: str, base: Optional[Path] = None) -> Path:
    p = Path(path_str).expanduser()
    if not p.is_absolute():
        p = (base or Path.cwd()) / p
    return p.resolve()


def _fmt_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes //= 1024
    return f"{size_bytes} PB"


def create_file(filename: str, content: str = "", **_) -> str:
    try:
        p = _safe_path(filename)
        if p.exists():
            return f"✗ File already exists: {p.name}"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        log.info("Created file: %s", p)
        return f"✓ File created: {p.name}"
    except OSError as e:
        log.error("create_file: %s", e)
        return f"✗ Could not create file: {e}"


def read_file(filename: str, **_) -> str:
    try:
        p = _safe_path(filename)
        if not p.exists():
            return f"✗ File not found: {filename}"
        if not p.is_file():
            return f"✗ Not a file: {filename}"
        content = p.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        preview = "\n".join(lines[:40])
        suffix = f"\n[... {len(lines) - 40} more lines ...]" if len(lines) > 40 else ""
        return f"📄 {p.name}\n{'─' * 50}\n{preview}{suffix}"
    except OSError as e:
        return f"✗ Could not read file: {e}"


def update_file(filename: str, **_) -> str:
    try:
        p = _safe_path(filename)
        if not p.exists():
            return f"✗ File not found: {filename}. Use 'create file {filename}' to create it."
        print(f"Enter new content for {p.name} (type END on a new line to finish):")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line == "END":
                break
            lines.append(line)
        content = "\n".join(lines)
        p.write_text(content, encoding="utf-8")
        log.info("Updated file: %s", p)
        return f"✓ File updated: {p.name} ({len(lines)} lines)"
    except OSError as e:
        return f"✗ Could not update file: {e}"


def append_file(filename: str, content: str = "", **_) -> str:
    try:
        p = _safe_path(filename)
        with p.open("a", encoding="utf-8") as f:
            f.write(content + "\n")
        return f"✓ Appended to: {p.name}"
    except OSError as e:
        return f"✗ Could not append: {e}"


def rename_file(source: str, destination: str, **_) -> str:
    try:
        src = _safe_path(source)
        dst = _safe_path(destination)
        if not src.exists():
            return f"✗ File not found: {source}"
        if dst.exists():
            return f"✗ Destination already exists: {destination}"
        src.rename(dst)
        log.info("Renamed %s -> %s", src, dst)
        return f"✓ Renamed: {src.name} → {dst.name}"
    except OSError as e:
        return f"✗ Rename failed: {e}"


def delete_file(filename: str, **_) -> str:
    try:
        p = _safe_path(filename)
        if not p.exists():
            return f"✗ File not found: {filename}"
        if not p.is_file():
            return f"✗ Not a file: {filename}"
        p.unlink()
        log.info("Deleted file: %s", p)
        return f"✓ File deleted: {p.name}"
    except OSError as e:
        return f"✗ Could not delete: {e}"


def copy_file(source: str, destination: str, **_) -> str:
    try:
        src = _safe_path(source)
        dst = _safe_path(destination)
        if not src.exists():
            return f"✗ Source not found: {source}"
        shutil.copy2(str(src), str(dst))
        log.info("Copied %s -> %s", src, dst)
        return f"✓ Copied: {src.name} → {dst.name}"
    except OSError as e:
        return f"✗ Copy failed: {e}"


def move_file(source: str, destination: str, **_) -> str:
    try:
        src = _safe_path(source)
        dst = _safe_path(destination)
        if not src.exists():
            return f"✗ Source not found: {source}"
        shutil.move(str(src), str(dst))
        log.info("Moved %s -> %s", src, dst)
        return f"✓ Moved: {src.name} → {dst.name}"
    except OSError as e:
        return f"✗ Move failed: {e}"


def create_folder(path: str, **_) -> str:
    try:
        p = _safe_path(path)
        if p.exists():
            return f"✗ Already exists: {p.name}"
        p.mkdir(parents=True, exist_ok=False)
        log.info("Created folder: %s", p)
        return f"✓ Folder created: {p.name}"
    except OSError as e:
        return f"✗ Could not create folder: {e}"


def delete_folder(path: str, **_) -> str:
    try:
        p = _safe_path(path)
        if not p.exists():
            return f"✗ Folder not found: {path}"
        if not p.is_dir():
            return f"✗ Not a folder: {path}"
        shutil.rmtree(str(p))
        log.info("Deleted folder: %s", p)
        return f"✓ Folder deleted: {p.name}"
    except OSError as e:
        return f"✗ Could not delete folder: {e}"


def list_files(path: Optional[str] = None, **_) -> str:
    target = _safe_path(path) if path else Path.cwd()
    try:
        if not target.exists():
            return f"✗ Path not found: {target}"
        items = sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        lines = [f"📂 {target}\n"]
        for item in items[:30]:
            icon = "📁" if item.is_dir() else "📄"
            size = _fmt_size(item.stat().st_size) if item.is_file() else ""
            lines.append(f"  {icon} {item.name:<40} {size}")
        if len(list(target.iterdir())) > 30:
            total = len(list(target.iterdir()))
            lines.append(f"  ... and {total - 30} more items")
        return "\n".join(lines)
    except PermissionError:
        return f"✗ Permission denied: {target}"
    except OSError as e:
        return f"✗ Error: {e}"


def recent_files(path: Optional[str] = None, count: str = "10", **_) -> str:
    target = _safe_path(path) if path else Path.cwd()
    n = int(count) if str(count).isdigit() else 10
    try:
        files_list = [(f, f.stat().st_mtime) for f in target.iterdir() if f.is_file()]
        files_list.sort(key=lambda x: x[1], reverse=True)
        if not files_list:
            return "No files found in directory."
        lines = [f"🕐 Recent files in {target}\n"]
        for f, mtime in files_list[:n]:
            ts = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            lines.append(f"  📄 {f.name:<40} {ts}")
        return "\n".join(lines)
    except OSError as e:
        return f"✗ Error: {e}"


def search_files(pattern: str, path: Optional[str] = None, **_) -> str:
    target = _safe_path(path) if path else Path.cwd()
    try:
        glob_pat = pattern if "*" in pattern or "?" in pattern else f"*{pattern}*"
        matches = list(target.rglob(glob_pat))[:50]
        if not matches:
            return f"No files matching '{pattern}' found."
        lines = [f"🔍 Search results for '{pattern}'\n"]
        for m in matches:
            lines.append(f"  {'📁' if m.is_dir() else '📄'} {m.relative_to(target)}")
        return "\n".join(lines)
    except OSError as e:
        return f"✗ Search error: {e}"


def open_file(filename: str, **_) -> str:
    try:
        p = _safe_path(filename)
        if not p.exists():
            return f"✗ File not found: {filename}"
        os.startfile(str(p))
        return f"✓ Opened: {p.name}"
    except OSError as e:
        return f"✗ Could not open: {e}"


def open_folder(path: str, **_) -> str:
    try:
        p = _safe_path(path)
        if not p.exists():
            return f"✗ Folder not found: {path}"
        os.startfile(str(p))
        return f"✓ Opened folder: {p.name}"
    except OSError as e:
        return f"✗ Could not open folder: {e}"


def navigate_to(path: str, _context=None, **_) -> str:
    try:
        p = _safe_path(path)
        if not p.is_dir():
            return f"✗ Directory not found: {path}"
        os.chdir(str(p))
        if _context:
            _context.update_cwd(p)
        return f"✓ Navigated to: {p}"
    except OSError as e:
        return f"✗ Navigation failed: {e}"


def file_info(path: str, **_) -> str:
    try:
        p = _safe_path(path)
        if not p.exists():
            return f"✗ Not found: {path}"
        st = p.stat()
        mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        ctime = datetime.datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"ℹ  File Information: {p.name}",
            f"   Path     : {p}",
            f"   Type     : {'Directory' if p.is_dir() else 'File'}",
            f"   Size     : {_fmt_size(st.st_size)}",
            f"   Modified : {mtime}",
            f"   Created  : {ctime}",
        ]
        return "\n".join(lines)
    except OSError as e:
        return f"✗ Could not get info: {e}"


def create_file_prompt(**_) -> str:
    try:
        name = input("Enter filename: ").strip()
        if not name:
            return "✗ No filename provided."
        return create_file(name)
    except (EOFError, KeyboardInterrupt):
        return "✗ Cancelled."


def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command("create_file", create_file, "Create a new file",
                     aliases=["create file", "make file", "new file"],
                     args_help="<filename>", category="Files"),
        make_command("create_file_prompt", create_file_prompt, "Create a new file (prompt for name)",
                     category="Files"),
        make_command("read_file", read_file, "Read and display a file",
                     aliases=["read file", "open file", "show file", "view file"],
                     args_help="<filename>", category="Files"),
        make_command("update_file", update_file, "Overwrite a file with new content",
                     aliases=["update file", "edit file", "write file"],
                     args_help="<filename>", category="Files"),
        make_command("append_file", append_file, "Append text to a file",
                     args_help="<filename> <content>", category="Files"),
        make_command("rename_file", rename_file, "Rename or move a file",
                     aliases=["rename file", "move file to"],
                     args_help="<source> <destination>", category="Files"),
        make_command("delete_file", delete_file, "Delete a file",
                     aliases=["delete file", "remove file"],
                     args_help="<filename>", category="Files",
                     permission=PermissionLevel.CONFIRM),
        make_command("copy_file", copy_file, "Copy a file",
                     aliases=["copy file"], args_help="<source> <destination>", category="Files"),
        make_command("move_file", move_file, "Move a file to a new location",
                     args_help="<source> <destination>", category="Files",
                     permission=PermissionLevel.CONFIRM),
        make_command("create_folder", create_folder, "Create a new folder",
                     aliases=["create folder", "make folder", "new folder", "mkdir"],
                     args_help="<path>", category="Files"),
        make_command("delete_folder", delete_folder, "Delete a folder and all contents",
                     args_help="<path>", category="Files",
                     permission=PermissionLevel.DANGEROUS),
        make_command("list_files", list_files, "List files in a directory",
                     aliases=["list files", "ls", "dir", "show files"],
                     args_help="[path]", category="Files"),
        make_command("recent_files", recent_files, "Show recently modified files",
                     aliases=["recent files"], args_help="[path]", category="Files"),
        make_command("search_files", search_files, "Search for files by name pattern",
                     aliases=["search files", "find files"],
                     args_help="<pattern>", category="Files"),
        make_command("open_file", open_file, "Open a file with its default application",
                     args_help="<filename>", category="Files"),
        make_command("open_folder", open_folder, "Open a folder in Explorer",
                     args_help="<path>", category="Files"),
        make_command("navigate_to", navigate_to, "Change current working directory",
                     aliases=["navigate to", "go to", "cd"],
                     args_help="<path>", category="Files"),
        make_command("file_info", file_info, "Show file or folder details",
                     aliases=["file info"], args_help="<path>", category="Files"),
    ])
