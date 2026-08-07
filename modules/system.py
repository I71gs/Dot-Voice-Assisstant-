"""
modules/system.py — DOT System Management Module

System info, power management, and OS controls.
"""

from __future__ import annotations

import os
import socket
import subprocess
from typing import Optional

import psutil
import requests

from core.command_registry import CommandRegistry, make_command
from core.logger import get_logger
from core.permissions import PermissionLevel

log = get_logger("system")


def system_info(**_) -> str:
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        lines = [
            "💻 SYSTEM INFORMATION",
            "─" * 40,
            f"  CPU Usage   : {cpu:.1f}%",
            f"  RAM Usage   : {mem.percent:.1f}%  ({mem.used // 1024**3:.1f} / {mem.total // 1024**3:.1f} GB)",
            f"  Disk Usage  : {disk.percent:.1f}%  ({disk.used // 1024**3:.1f} / {disk.total // 1024**3:.1f} GB)",
        ]
        try:
            bat = psutil.sensors_battery()
            if bat:
                plug = "🔌 Plugged in" if bat.power_plugged else "🔋 On battery"
                lines.append(f"  Battery     : {bat.percent:.0f}%  {plug}")
        except AttributeError:
            pass
        return "\n".join(lines)
    except Exception as e:
        return f"✗ Could not retrieve system info: {e}"


def cpu_usage(**_) -> str:
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        count = psutil.cpu_count()
        freq = psutil.cpu_freq()
        lines = [
            f"🖥  CPU Usage: {cpu:.1f}%",
            f"   Cores    : {count}",
        ]
        if freq:
            lines.append(f"   Frequency: {freq.current:.0f} MHz")
        return "\n".join(lines)
    except Exception as e:
        return f"✗ CPU info error: {e}"


def ram_usage(**_) -> str:
    try:
        mem = psutil.virtual_memory()
        return (
            f"🧠 RAM Usage: {mem.percent:.1f}%\n"
            f"   Used : {mem.used // 1024**3:.2f} GB\n"
            f"   Total: {mem.total // 1024**3:.2f} GB\n"
            f"   Free : {mem.available // 1024**3:.2f} GB"
        )
    except Exception as e:
        return f"✗ RAM info error: {e}"


def disk_usage(path: Optional[str] = None, **_) -> str:
    try:
        target = path or "/"
        disk = psutil.disk_usage(target)
        return (
            f"💾 Disk Usage ({target}): {disk.percent:.1f}%\n"
            f"   Used : {disk.used // 1024**3:.2f} GB\n"
            f"   Total: {disk.total // 1024**3:.2f} GB\n"
            f"   Free : {disk.free // 1024**3:.2f} GB"
        )
    except Exception as e:
        return f"✗ Disk info error: {e}"


def battery_status(**_) -> str:
    try:
        bat = psutil.sensors_battery()
        if bat is None:
            return "ℹ  No battery detected (desktop system)"
        plug = "Plugged in 🔌" if bat.power_plugged else "On battery 🔋"
        secs = bat.secsleft
        if secs > 0:
            h, m = divmod(secs // 60, 60)
            time_left = f"{h}h {m}m remaining"
        else:
            time_left = "Calculating..." if not bat.power_plugged else "Charging"
        return f"🔋 Battery: {bat.percent:.0f}%  |  {plug}  |  {time_left}"
    except Exception as e:
        return f"✗ Battery error: {e}"


def network_info(**_) -> str:
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        lines = [
            "🌐 NETWORK INFORMATION",
            "─" * 40,
            f"  Hostname   : {hostname}",
            f"  Local IP   : {ip}",
        ]
        try:
            resp = requests.get("https://api.ipify.org", timeout=3)
            lines.append(f"  Public IP  : {resp.text.strip()}")
        except Exception:
            lines.append("  Public IP  : (unavailable)")
        try:
            requests.get("https://google.com", timeout=2)
            lines.append("  Internet   : ✓ Connected")
        except Exception:
            lines.append("  Internet   : ✗ No connection")
        return "\n".join(lines)
    except Exception as e:
        return f"✗ Network info error: {e}"


def running_processes(**_) -> str:
    try:
        procs = []
        for p in psutil.process_iter(["pid", "name", "memory_percent", "cpu_percent"]):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x.get("memory_percent") or 0, reverse=True)
        lines = [f"⚙  Top 15 Running Processes\n  {'PID':<8} {'Name':<30} {'RAM%':<8} {'CPU%'}"]
        lines.append("  " + "─" * 60)
        for p in procs[:15]:
            lines.append(
                f"  {p.get('pid', ''):<8} {(p.get('name') or ''):<30} "
                f"{p.get('memory_percent') or 0:.1f}%{' ':4}"
                f"{p.get('cpu_percent') or 0:.1f}%"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"✗ Process error: {e}"


def shutdown(delay: Optional[str] = None, **_) -> str:
    secs = int(delay) if delay and str(delay).isdigit() else 10
    try:
        os.system(f"shutdown /s /t {secs}")
        log.warning("Shutdown scheduled in %ds", secs)
        return f"⚠ Shutting down in {secs} seconds. Type 'cancel shutdown' to abort."
    except Exception as e:
        return f"✗ Shutdown error: {e}"


def restart(delay: Optional[str] = None, **_) -> str:
    secs = int(delay) if delay and str(delay).isdigit() else 10
    try:
        os.system(f"shutdown /r /t {secs}")
        log.warning("Restart scheduled in %ds", secs)
        return f"⚠ Restarting in {secs} seconds. Type 'cancel shutdown' to abort."
    except Exception as e:
        return f"✗ Restart error: {e}"


def cancel_shutdown(**_) -> str:
    try:
        result = subprocess.run("shutdown /a", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return "✓ Shutdown/restart cancelled."
        return "ℹ  No pending shutdown to cancel."
    except Exception as e:
        return f"✗ Cancel error: {e}"


def lock_computer(**_) -> str:
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        log.info("Computer locked")
        return "✓ Computer locked."
    except Exception as e:
        return f"✗ Lock error: {e}"


def sleep(**_) -> str:
    try:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "✓ Sleeping..."
    except Exception as e:
        return f"✗ Sleep error: {e}"


def set_brightness(level: str, **_) -> str:
    try:
        lvl = int(level)
        if not (0 <= lvl <= 100):
            return "✗ Brightness must be 0–100."
        script = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {lvl})"
        subprocess.run(["powershell", "-Command", script], capture_output=True, timeout=5)
        return f"✓ Brightness set to {lvl}%"
    except Exception as e:
        return f"✗ Brightness error: {e}"


def register_commands(registry: CommandRegistry, scheduler=None) -> None:
    registry.register_all([
        make_command("system_info", system_info, "Show CPU, RAM, disk, and battery",
                     aliases=["system info", "sysinfo", "sys info"],
                     category="System"),
        make_command("cpu_usage", cpu_usage, "Show CPU usage and frequency",
                     aliases=["cpu", "cpu usage"],
                     category="System"),
        make_command("ram_usage", ram_usage, "Show RAM usage",
                     aliases=["ram", "memory"],
                     category="System"),
        make_command("disk_usage", disk_usage, "Show disk usage",
                     aliases=["disk", "storage"],
                     args_help="[path]", category="System"),
        make_command("battery_status", battery_status, "Show battery level and status",
                     aliases=["battery"],
                     category="System"),
        make_command("network_info", network_info, "Show network and internet status",
                     aliases=["network info", "net info", "netinfo"],
                     category="System"),
        make_command("running_processes", running_processes, "List top running processes",
                     aliases=["processes", "ps"],
                     category="System"),
        make_command("shutdown", shutdown, "Shut down the computer",
                     args_help="[delay_seconds]", category="System",
                     permission=PermissionLevel.DANGEROUS),
        make_command("restart", restart, "Restart the computer",
                     aliases=["reboot"],
                     args_help="[delay_seconds]", category="System",
                     permission=PermissionLevel.DANGEROUS),
        make_command("cancel_shutdown", cancel_shutdown, "Cancel a scheduled shutdown/restart",
                     aliases=["cancel shutdown", "abort shutdown"],
                     category="System"),
        make_command("lock_computer", lock_computer, "Lock the screen",
                     aliases=["lock", "lock computer", "lock screen"],
                     category="System"),
        make_command("sleep", sleep, "Put the computer to sleep",
                     aliases=["hibernate"],
                     category="System",
                     permission=PermissionLevel.CONFIRM),
        make_command("set_brightness", set_brightness, "Set screen brightness (0-100)",
                     aliases=["brightness"],
                     args_help="<level>", category="System"),
    ])
