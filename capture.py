# -*- coding: utf-8 -*-
"""Capture quotidienne BRUTE des 5 bourses africaines a « API jour courant ».

Tourne dans GitHub Actions (gratuit) : ces API (NGX, ZSE, BSE, USE, MSE) ne
servent que la seance du jour — un jour non capture est perdu a jamais. Ce
script archive les REPONSES BRUTES dans snapshots/AAAA-MM-JJ/ ; le PC local
les importe et les parse a sa prochaine mise a jour (l'analyse vit la-bas,
ici on ne fait que conserver).

Volontairement en bibliotheque standard uniquement (urllib) : rien a installer.
"""
from __future__ import annotations

import datetime
import json
import ssl
import sys
import time
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
RETRIES = 3
TIMEOUT = 45


def fetch(url: str, *, data: bytes | None = None, insecure: bool = False,
          content_type: str | None = None) -> bytes:
    ctx = ssl.create_default_context()
    if insecure:  # MSE : chaine TLS incomplete cote serveur
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    headers = {"User-Agent": UA}
    if content_type:
        headers["Content-Type"] = content_type
    last: Exception | None = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
                if r.status != 200:
                    raise RuntimeError(f"HTTP {r.status}")
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < RETRIES - 1:
                time.sleep(5 * (attempt + 1))
    raise last  # type: ignore[misc]


def main() -> int:
    today = datetime.date.today()
    if today.weekday() >= 5:  # ceinture en plus du cron 1-5
        print("week-end, rien a capturer")
        return 0
    out = Path("snapshots") / today.isoformat()
    out.mkdir(parents=True, exist_ok=True)

    jobs = {
        "ngx.json": lambda: fetch(
            "https://doclib.ngxgroup.com/REST/api/statistics/equities/"
            "?market=&sector=&orderby=&pageSize=300&pageNo=0"),
        "zse.json": lambda: fetch(
            "https://ds88jcmqc11je.cloudfront.net/api/fetch/price-sheet?exchange=ZSE"),
        "bse_domestic.json": lambda: fetch(
            "https://apis.bse.co.bw/api/v1/market-overview",
            data=json.dumps({"board": "domestic"}).encode(),
            content_type="application/json"),
        "bse_foreign.json": lambda: fetch(
            "https://apis.bse.co.bw/api/v1/market-overview",
            data=json.dumps({"board": "foreign"}).encode(),
            content_type="application/json"),
        "use.json": lambda: fetch("https://use.or.ug/api/delayed-data"),
        "mse.html": lambda: fetch("https://mse.co.mw/market/mainboard", insecure=True),
    }

    ok, failed = [], []
    for name, job in jobs.items():
        try:
            payload = job()
            (out / name).write_bytes(payload)
            ok.append(name)
            print(f"OK    {name}  {len(payload)} octets")
        except Exception as e:  # noqa: BLE001
            failed.append(name)
            print(f"ECHEC {name}  {e}")

    (out / "meta.json").write_text(json.dumps({
        "captured_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "ok": ok, "failed": failed,
    }, indent=1))

    # un echec partiel n'est pas fatal (on garde ce qu'on a) ; tout-echec = rouge
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
