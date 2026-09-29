# AGENTS.md — ideas-locas-20 (Laya / Jev experiments)

## What this project is

Experiments against a local **Laya** server (Jev-compatible protocol) that answers
structured yes/no and choice questions over a free-text `state`, hosted for free on the
Spark. No backend, no frontend, no tests: a handful of standalone Python scripts that
talk to that server. The server address lives in `.env` (never hardcoded in files).

## Architecture (as defined by `laya-hector.py`)

The `.py` experiment files are independent, disposable CLI scripts. A single shared
stdlib module, `laya_base.py`, centralizes base-URL resolution so every script shares the
exact same config source. The canonical experiment shape to copy is `laya-hector.py`.

- **Stdlib only**: `urllib.request` + `json` + `time`. No `requests`, no SDK, no local
  packages, no dotenv library. Every script runs with bare `python3`; `.venv-laya/` is
  not needed at runtime.
- **Centralized base URL** via `laya_base.py`, which exports `BASE`, `URL` and `HEALTH`
  with this precedence: `LAYA_BASE` env var → `LAYA_BASE=...` in the project-root `.env` →
  default `http://localhost:8432`. Experiment scripts do `from laya_base import URL` (and
  `HEALTH` where the health endpoint is used) and `POST {URL}` = `{BASE}/v1/systemone`.
  Never hardcode intranet IPs in versioned files (security: repo may be public); the real
  address lives in `.env` (git-ignored).
- **Protocol** (Jev `POST /v1/systemone`):
  - Request: `{"state": <string>, "questions": {<name>: {"type": ..., "instructions": <str>, ...}}}`
  - Question `type`:
    - `"choice"` — add `"criteria": {<label>: <description>}`; answer is one label + `confidence`.
    - `"noul"` — yes/no decision with probability; answer is `noul` (P(yes)).
    - `"score"` — numeric score; answer includes `answer_confidence`.
  - Response: `{"answers": {<name>: {...}}, "routing": {"model": <str>}}`.
- **Helper structure** worth keeping (from `laya-hector.py`):
  - `predict(state, questions) -> (data, ms)` — one POST, returns parsed JSON + latency in ms.
  - `show(...)` — prints a one-line result, tolerating all three answer shapes (`choice` / `noul` / `score`).
  - Experiment body is a sequence of **named example sections** (`== Ejemplo 1 · ... ==`) — each
    section is self-contained state + questions + print. Run = `python3 <script>.py`.

## Conventions for new agents

- Add new experiments as a **new standalone `.py` file** in the project root (pattern:
  `laya-<theme>.py`), not by growing an existing one.
- New scripts MUST be runnable with the system `python3` and must not add
  dependencies to `.venv-laya` (the package inside is legacy/unused since all
  scripts now go over HTTP).
- **Config resolution**: scripts import `URL` (and `HEALTH`) from `laya_base.py`, which
  reads `LAYA_BASE` from an env var first, then the project-root `.env`, then localhost.
  Put the real intranet address in `.env` (git-ignored); never in versioned code.
- Comments and user-facing prints in Spanish, identifiers in English (current style).
- Do **not** commit `.venv-laya/` or `.env` (both ignored by git). `.env.example` is tracked.

## File map

| File | Role |
|------|------|
| `laya_base.py` | Shared stdlib config: resolves `BASE`/`URL`/`HEALTH` from env → `.env` → localhost |
| `laya-hector.py` | Reference architecture: examples from hdeleon's video (`choice` type: beer for fish tacos, spam classifier) |
| `laya-client.py` | ES/EN yes/no test cases (`noul` type) with health check |
| `laya-demo.py` | Minimal `noul` example (double-charge ES case) over the same protocol |
| `.env` | Local config holding the real `LAYA_BASE`. **Git-ignored — never commit.** |
| `.env.example` | Tracked template to copy into `.env` |
| `.venv-laya/` | venv (Python 3.13) holding the legacy `laya` package |

## How to run

```bash
# 1) Point at your server (once): copy the template and fill in the real address
cp .env.example .env          # then edit .env → LAYA_BASE=http://<ip-spark>:8432
#    (or export LAYA_BASE for the session instead; either wins the precedence order)

# 2) Run any script (server must be up)
python3 laya-hector.py
python3 laya-client.py
python3 laya-demo.py
```
