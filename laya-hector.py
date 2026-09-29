"""Recreación de los ejemplos del video de Héctor de León (hdeleon.net):
'¿Adiós Jev? Laya ha llegado y es GRATIS'.

Base URL configurable (por defecto localhost; en la intranet: LAYA_BASE=http://<ip-spark>:8432).
"""
import json
import time
import urllib.request

from laya_base import BASE, URL  # noqa: F401  (BASE por compatibilidad con la arquitectura)


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
    q = name
    a = data["answers"][q]
    ruta = "choice" if "choice" in a else ("noul" if "noul" in a else "score")
    val = a.get("choice", a.get("noul"))
    conf = a.get("confidence", a.get("answer_confidence"))
    print(f"  {state[:60]!r:64s} → {val}   (conf={conf:.2f}, {ms:.0f} ms, modelo={data['routing']['model']})")


# --- Ejemplo 1: la cerveza para tacos de pescado (tipo `choice`) ------------
state1 = "Quiero una cerveza ligera y refrescante para tomar unos tacos de pescado."
q1 = {
    "categoría": {
        "type": "choice",
        "instructions": "¿Qué tipo de cerveza corresponde a esa necesidad?",
        "criteria": {
            "lager": "cerveza ligera, limpia y refrescante",
            "IPA": "cerveza amarga, con lúpulo intenso y aromática",
            "stout": "cerveza oscura, fuerte, con notas de café y chocolate",
            "wheat": "cerveza de trigo, turbia, suave y ligeramente dulce",
        },
    }
}

print("== Ejemplo 1 · Cerveza para tacos de pescado ==")
d, ms = predict(state1, q1)
show(state1, "categoría", d, ms)

# --- Ejemplo 2: clasificador de spam en asuntos de correo ---------------------
ASUNTOS = [
    "URGENTE: Tu cuenta será bloqueada",
    "Tu pedido fue enviado, llegará entre el martes y miércoles",
    "Oferta exclusiva: duplica tu dinero hoy",
    "Hola, confirmo nuestra reunión",
    "¡Ganaste un iPhone gratis!",
]
q2 = {
    "spam": {
        "type": "choice",
        "instructions": "¿Este asunto de correo parece spam?",
        "criteria": {"spam": "mensajes de engaño, urgencia falsa o premios", "no_spam": "comunicación normal y legítima"},
    }
}

print("\n== Ejemplo 2 · Spam / no spam ==")
for a in ASUNTOS:
    d, ms = predict(a, {n: v for n, v in q2.items()})
    show(a, "spam", d, ms)
