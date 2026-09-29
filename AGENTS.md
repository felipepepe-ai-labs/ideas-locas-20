# AGENTS.md — ideas-locas-20 (Laya / Jev experiments)

## What this project is

Experiments against a local **Laya** server (Jev-compatible protocol) that answers
structured yes/no and choice questions over a free-text `state`, hosted for free on the
Spark (set `LAYA_BASE` to its address and port; no hardcoded intranet IPs in files).
No backend, no frontend, no tests: a handful of standalone Python scripts that talk
to that server.

## Architecture (as defined by `laya-hector.py`)

The files are independent, disposable CLI scripts. The canonical shape to copy is
`laya-hector.py`:

- **Stdlib only**: `urllib.request` + `json` + `time`. No `requests`, no SDK, no local
  packages. This is deliberate — every script must run with bare `python3` and
  `.venv-laya/` is not needed at runtime.
- **Configurable base URL at the top**: `BASE = os.environ.get("LAYA_BASE", "http://localhost:8432")`,
  endpoints are `{BASE}/v1/systemone` and `{BASE}/health`. Never hardcode intranet IPs in files
  (security: repo may be public). On the intranet, export `LAYA_BASE` before running.
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
  - Script body is a sequence of **named example sections** (`== Ejemplo 1 · ... ==`) — each
    section is self-contained state + questions + print. Run = `python3 <script>.py`.

## Conventions for new agents

- Add new experiments as a **new standalone `.py` file** in the project root (pattern:
  `laya-<theme>.py`), not by growing an existing one.
- New scripts MUST be runnable with the system `python3` and must not add
  dependencies to `.venv-laya` (the package inside is legacy/unused since all
  scripts now go over HTTP).
- **Configurable base URL**: scripts read `LAYA_BASE` (default `http://localhost:8432`).
  Intrusion IP, never in files; set `LAYA_BASE` before running on the intranet.
- Comments and user-facing prints in Spanish, identifiers in English (current style).
- Do **not** commit `.venv-laya/` (ignored by git).

## File map

| File | Role |
|------|------|
| `laya-hector.py` | Reference architecture: examples from hdeleon's video (`choice` type: beer for fish tacos, spam classifier) |
| `laya-client.py` | ES/EN yes/no test cases (`noul` type) with health check |
| `laya-demo.py` | Minimal `noul` example (double-charge ES case) over the same protocol |
| `.venv-laya/` | venv (Python 3.13) holding the `laya` package |

## How to run

```bash
# server must be up on the Spark — export the base URL for intranet runs
export LAYA_BASE=http://<ip-spark>:8432

python3 laya-hector.py
python3 laya-client.py
python3 laya-demo.py
```
