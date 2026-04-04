from __future__ import annotations

import platform
import shutil
import subprocess
from contextlib import contextmanager
from typing import Iterator


def _dns_sd_path() -> str | None:
    return shutil.which("dns-sd") or shutil.which("dns-sd.exe")


def _avahi_publish_path() -> str | None:
    return shutil.which("avahi-publish-service")


def _detect_backend() -> str | None:
    """Detect available mDNS backend: 'dns-sd', 'avahi', or None."""
    system = platform.system()
    if system == "Darwin" and _dns_sd_path():
        return "dns-sd"
    if system == "Windows" and _dns_sd_path():
        return "dns-sd"
    if system == "Linux" and _avahi_publish_path():
        return "avahi"
    return None


def bonjour_available() -> bool:
    return _detect_backend() is not None


def _build_dns_sd_cmd(
    *, role: str, port: int, path: str, product: str, version: str
) -> list[str]:
    """Build dns-sd command (macOS / Windows)."""
    return [
        _dns_sd_path() or "dns-sd",
        "-R",
        f"ariaflow-{role}",
        "_ariaflow._tcp",
        "local",
        str(port),
        f"role={role}",
        f"path={path}",
        f"product={product}",
        f"version={version}",
        "proto=http",
    ]


def _build_avahi_cmd(
    *, role: str, port: int, path: str, product: str, version: str
) -> list[str]:
    """Build avahi-publish-service command (Linux)."""
    return [
        _avahi_publish_path() or "avahi-publish-service",
        f"ariaflow-{role}",
        "_ariaflow._tcp",
        str(port),
        f"role={role}",
        f"path={path}",
        f"product={product}",
        f"version={version}",
        "proto=http",
    ]


@contextmanager
def advertise_http_service(
    *, role: str, port: int, path: str, product: str, version: str
) -> Iterator[None]:
    backend = _detect_backend()
    if backend is None:
        yield
        return
    if backend == "avahi":
        cmd = _build_avahi_cmd(
            role=role, port=port, path=path, product=product, version=version
        )
    else:
        cmd = _build_dns_sd_cmd(
            role=role, port=port, path=path, product=product, version=version
        )
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        yield
    finally:
        try:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
        except Exception:
            pass
