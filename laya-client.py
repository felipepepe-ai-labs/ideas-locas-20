"""Casos `noul` (decisión sí/no con probabilidad) contra el servidor
Laya, con y sin inglés, con chequeo de salud previo.

Base URL configurable (por defecto localhost; en la intranet: LAYA_BASE=http://<ip-spark>:8432).
"""
import json
import os
import time
import urllib.request

BASE = os.environ.get("LAYA_BASE", "http://localhost:8432")
URL = f"{BASE}/v1/systemone"


def predict(state, questions):
    payload = {"state": state, "questions": questions}
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    ms = (time.perf_counter() - t0) * 1000
    return data, ms


def show(state, name, data, ms):
    a = data["answers"][name]
    val = a.get("choice", a.get("noul", a.get("score")))
    conf = a.get("confidence", a.get("answer_confidence"))
    conf_s = f"conf={conf:.2f}, " if conf is not None else ""
    print(f"  {state[:60]!r:64s} → {val}   ({conf_s}{ms:.0f} ms, modelo={data['routing']['model']})")


# --- Salud ------------------------------------------------------------------
print("== Salud del servidor ==")
with urllib.request.urlopen(f"{BASE}/health", timeout=10) as r:
    h = json.loads(r.read())
print(f"  ok | device={h['device']} | loaded={h['loaded']}")

# --- Doble cobro: ¿cancela y/o pide reembolso? (ES) --------------------------
NUL = [
    ("cancela", "¿La persona amenaza con cancelar o irse?"),
    ("pide_reembolso", "¿Pide explícitamente un reembolso?"),
]

print("\n== noul · Doble cobro (ES) ==")
es = (
    "Me cobraron dos veces por marzo. Devuélvenme la duplicidad hoy "
    "o cancelo el plan la semana que viene."
)
q = {n: {"type": "noul", "instructions": i} for n, i in NUL}
d, ms = predict(es, q)
for n in q:
    show(es, n, d, ms)

# --- Doble cobro: ¿cancela y/o pide reembolso? (EN) --------------------------
print("\n== noul · Doble cobro (EN) ==")
en = (
    "I was charged twice for March. Refund the duplicate today "
    "or I'm cancelling my plan next week."
)
d, ms = predict(en, q)
for n in q:
    show(en, n, d, ms)
