#!/usr/bin/env python3
"""
Esporta i fogli Google in JSON per la dashboard DatAmaranto.
Fonte: Dataset Reggina 2026/27
"""

import csv
import io
import json
import os
import sys
import urllib.request

SHEET_ID = "1oYEWtlr7rKcuzU_B5P8FBB-AydciGH08NjEsm8XOzVE"

# nome_file_json : gid della scheda
FOGLI = {
    "rosa-anagrafica.json": "0",           # 👤 Rosa
    "calendario.json":      "1220754771",  # 📅 Calendario
    "minuti-gol.json":      "546570041",   # 🎯 DettaglioMatch
}

URL = "https://docs.google.com/spreadsheets/d/{id}/export?format=csv&gid={gid}"


def scarica_csv(gid):
    url = URL.format(id=SHEET_ID, gid=gid)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}")
        return resp.read().decode("utf-8-sig")


def csv_to_records(testo):
    righe = list(csv.reader(io.StringIO(testo)))
    if not righe:
        return []

    intestazioni = [h.strip() for h in righe[0]]

    records = []
    for riga in righe[1:]:
        # salta le righe completamente vuote
        if not any(c.strip() for c in riga):
            continue
        rec = {}
        for i, testa in enumerate(intestazioni):
            if not testa:          # ignora colonne senza intestazione
                continue
            rec[testa] = riga[i].strip() if i < len(riga) else ""
        records.append(rec)
    return records


def main():
    errori = 0

    for nome_file, gid in FOGLI.items():
        try:
            testo = scarica_csv(gid)
            records = csv_to_records(testo)

            if not records:
                print(f"⚠  {nome_file}: 0 righe — file NON aggiornato per sicurezza")
                errori += 1
                continue

            nuovo = json.dumps(records, ensure_ascii=False, indent=1)

            # scrive solo se il contenuto è cambiato
            if os.path.exists(nome_file):
                with open(nome_file, "r", encoding="utf-8") as f:
                    if f.read() == nuovo:
                        print(f"=  {nome_file}: {len(records)} righe, nessuna modifica")
                        continue

            with open(nome_file, "w", encoding="utf-8") as f:
                f.write(nuovo)
            print(f"✓  {nome_file}: {len(records)} righe aggiornate")

        except Exception as e:
            print(f"✗  {nome_file}: errore — {e}")
            errori += 1

    if errori:
        sys.exit(1)


if __name__ == "__main__":
    main()
