"""Demo Laya: decisión sí/no con probabilidad (tipo `noul`).

Base URL configurable (por defecto localhost; en la intranet: LAYA_BASE=http://<ip-spark>:8432).
"""
import json
import time
import urllib.request

from laya_base import URL  # noqa: F401  (URL derivada de LAYA_BASE/.env)


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


# --- noul · Doble cobro: ¿cancela y/o pide reembolso? ------------------------
state = (
    "Me cobraron dos veces por marzo. Devuélvenme la duplicidad hoy "
    "o cancelo el plan la semana que viene."
)
questions = {
    "cancela": {
        "type": "noul",
        "instructions": "¿La persona amenaza con cancelar o irse?",
    },
    "pide_reembolso": {
        "type": "noul",
        "instructions": "¿Pide explícitamente un reembolso?",
    },
}

print("== noul · Doble cobro ==")
d, ms = predict(state, questions)
for name in questions:
    show(state, name, d, ms)
