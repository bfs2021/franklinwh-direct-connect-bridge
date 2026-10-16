"""Entrypoint: `franklinwh-direct-connect-bridge run` → serve the FastAPI app via uvicorn."""

from __future__ import annotations

import argparse
import logging

import uvicorn

from .config import get_settings


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="franklinwh-direct-connect-bridge")
    p.add_argument("command", nargs="?", default="run", choices=["run", "ping"])
    p.add_argument("host", nargs="?", help="ping: the aGate's address (default: FWH_HOST)")
    a = p.parse_args(argv)
    if a.command == "ping":
        return _ping(a.host or get_settings().fwh_host)

    s = get_settings()
    logging.basicConfig(
        level=getattr(logging, s.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    uvicorn.run("franklinwh_direct_connect_bridge.app:create_app", factory=True,
                host=s.http_host, port=s.http_port, log_level=s.log_level)
    return 0


def _ping(host: str) -> int:
    """`franklinwh-direct-connect-bridge ping [HOST]`: a timed ping and a timed connect to
    the Direct Connect port :9000 (#123). Never touches the aGate Modbus TCP Server :502."""
    from .diagnostics import probe
    if not host:
        print("no host: pass one, or set FWH_HOST")
        return 2
    r = probe(host)
    ping = f"ok {r['ping_ms']} ms" if r["ping"] else "no reply"
    dc = (f"ok {r['dc_9000_connect_ms']} ms" if r["dc_9000"] else "refused / timed out")
    print(f"{r['host']}\n  ping           {ping}\n  :9000 connect  {dc}")
    return 0 if r["dc_9000"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
