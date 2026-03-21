from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


ARIA2_LABEL = "com.ariaflow.aria2"
ARIAFLOW_LABEL = "com.ariaflow.serve"


def is_macos() -> bool:
    return os.uname().sysname.lower() == "darwin"


def brew_is_installed(package: str) -> bool:
    return shutil.which("brew") is not None and subprocess.call(["brew", "list", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def ensure_brew_tap(tap: str = "bonomani/ariaflow", dry_run: bool = False) -> list[str]:
    commands = [["brew", "tap", tap]]
    if dry_run:
        return [" ".join(cmd) for cmd in commands]
    subprocess.run(commands[0], check=True)
    return [" ".join(commands[0])]


def homebrew_install_ariaflow(dry_run: bool = False) -> list[str]:
    commands = [["brew", "tap", "bonomani/ariaflow"], ["brew", "install", "ariaflow"]]
    if dry_run:
        return [" ".join(cmd) for cmd in commands]
    for cmd in commands:
        subprocess.run(cmd, check=True)
    return [" ".join(cmd) for cmd in commands]


def homebrew_update_ariaflow(dry_run: bool = False) -> list[str]:
    commands = [["brew", "upgrade", "ariaflow"]]
    if dry_run:
        return [" ".join(cmd) for cmd in commands]
    try:
        subprocess.run(commands[0], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["brew", "install", "ariaflow"], check=True)
    return [" ".join(cmd) for cmd in commands]


def launch_agents_dir() -> Path:
    return Path.home() / "Library" / "LaunchAgents"


def aria2_plist_path() -> Path:
    return launch_agents_dir() / f"{ARIA2_LABEL}.plist"


def ariaflow_plist_path() -> Path:
    return launch_agents_dir() / f"{ARIAFLOW_LABEL}.plist"


def aria2_session_dir() -> Path:
    return Path.home() / ".aria2"


def install_aria2_launchd(dry_run: bool = False) -> list[str]:
    bin_path = shutil.which("aria2c") or "/opt/homebrew/bin/aria2c"
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{ARIA2_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{bin_path}</string>
    <string>--enable-rpc=true</string>
    <string>--rpc-listen-all=false</string>
    <string>--rpc-listen-port=6800</string>
    <string>--rpc-allow-origin-all=true</string>
    <string>--console-log-level=warn</string>
    <string>--summary-interval=0</string>
    <string>--dir={str(Path.home() / "Downloads")}</string>
    <string>--input-file={str(aria2_session_dir() / "session.txt")}</string>
    <string>--save-session={str(aria2_session_dir() / "session.txt")}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
"""
    commands = [
        f"mkdir -p {aria2_session_dir()} {Path.home() / 'Downloads'} {launch_agents_dir()}",
        f"touch {aria2_session_dir() / 'session.txt'}",
        f"cat > {aria2_plist_path()} <<'PLIST'\n{plist}PLIST",
        f"launchctl load {aria2_plist_path()}",
    ]
    if dry_run:
        return commands
    subprocess.run(["mkdir", "-p", str(aria2_session_dir()), str(Path.home() / "Downloads"), str(launch_agents_dir())], check=True)
    (aria2_session_dir() / "session.txt").touch(exist_ok=True)
    aria2_plist_path().write_text(plist, encoding="utf-8")
    subprocess.run(["launchctl", "load", str(aria2_plist_path())], check=True)
    return commands


def install_ariaflow_launchd(dry_run: bool = False) -> list[str]:
    bin_path = shutil.which("ariaflow") or "/opt/homebrew/bin/ariaflow"
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{ARIAFLOW_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{bin_path}</string>
    <string>serve</string>
    <string>--host</string>
    <string>127.0.0.1</string>
    <string>--port</string>
    <string>8000</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
"""
    commands = [
        f"mkdir -p {launch_agents_dir()}",
        f"cat > {ariaflow_plist_path()} <<'PLIST'\n{plist}PLIST",
        f"launchctl load {ariaflow_plist_path()}",
    ]
    if dry_run:
        return commands
    subprocess.run(["mkdir", "-p", str(launch_agents_dir())], check=True)
    ariaflow_plist_path().write_text(plist, encoding="utf-8")
    subprocess.run(["launchctl", "load", str(ariaflow_plist_path())], check=True)
    return commands


def install_all(dry_run: bool = False) -> dict[str, list[str]]:
    if not dry_run and not is_macos():
        raise RuntimeError("install is only supported on macOS")
    return {
        "ariaflow": homebrew_install_ariaflow(dry_run=dry_run),
        "aria2-launchd": install_aria2_launchd(dry_run=dry_run),
        "ariaflow-serve-launchd": install_ariaflow_launchd(dry_run=dry_run),
    }
