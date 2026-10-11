# SpinDoctor Qwerty for Devin CLI

**Devin CLI plugin for the SpinDoctor 3.1.2 quantum-circuit simulator.** It adds a skill, a triggered rule, a custom subagent
and a local MCP server with six tools to the [Devin CLI](https://docs.devin.ai/cli/extensibility/plugins/overview) (and Devin
Desktop): build and run `q.*` circuits (1-298 logical qubits), run the 241 built-in presets, process folders of command files
with `q.folder`, test theories from files, pasted text or the conversation itself, and get TXT, PDF, JSON and CSV reports.
Everything runs locally in a bundled, standard-library-only Python engine.

> **Honest limits:** SpinDoctor is a **classical** FP64 simulator running on your computer. It is not a quantum computer, does not
> connect to quantum hardware and gives no quantum speed-up or advantage. Registers hold 1-298 logical qubits, but one entangled
> group (factor) is limited to 59 qubits and dense factors to the memory budget (2^n x 16 bytes); registers wider than 29 qubits
> sample in basis Z only. Histograms come from seeded Born sampling. Requires **Python 3.8+** (no packages).

Version **1.1.0** (engine 1.1.0, "SpinDoctor 3.1.2 parity"). Author: RUSSELL PHILIP SMITHSON. License: GPL-3.0-or-later.

## What's in the plugin

The repo root is a plugin in the **Agent Plugins 1.0.0** layout (root `plugin.json` + `mcp.json`), one of the formats the Devin CLI
loads. It's the only Devin layout for which the docs say `${PLUGIN_ROOT}` is expanded in MCP server configs and the server
starts in the plugin folder.

| Part | File | What it does |
|---|---|---|
| Manifest | `plugin.json` | Name, version, description, author, homepage, repository, license, keywords (Agent Plugins 1.0.0 schema) |
| MCP server | `mcp.json` | Starts `python3 ${PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py` (stdio) |
| Skill | `skills/spindoctor-qwerty/` | Instructions, honesty rules, the engine and its CLI; available as `/spindoctor-qwerty:spindoctor-qwerty` |
| Rule | `rules/spindoctor-qwerty.md` | `trigger: model_decision`: honesty rules, q.* grammar, function table and theory-testing steps, applied when relevant |
| Subagent | `agents/qwerty-helper.md` | `spindoctor-qwerty:qwerty-helper`: runs scripts, presets, folders and theory tests and explains them |
| Python switch | `tools/set_python.py` | Changes the server's Python command (for Windows) |

No hooks, no `AGENTS.md` (it would add an always-on rule to every session), no secrets, no network access, no telemetry. Nothing
runs until the agent calls a tool or you use the skill. Reports go to `~/spindoctor-workspace` (set `SPINDOCTOR_WORKSPACE` to
change it). The server runs with the plugin folder as its working directory, so give absolute paths for files and folders.

## Install

You need the Devin CLI (signed in: managing plugins requires `devin auth login`) and Python 3.8+ (as `python3` on macOS/Linux; see
Windows below).

**From GitHub:**

```sh
devin plugins install LKVexa/spindoctor-qwerty-devin-cli
devin plugins info spindoctor-qwerty
```

This records the plugin in your personal manifest, so it loads on every machine you sign in to. Pin a commit if you like, or use
`--local` to install on this machine only.

**From a local checkout (this machine only, linked to the folder):**

```sh
git clone https://github.com/LKVexa/spindoctor-qwerty-devin-cli
devin plugins install --local ./spindoctor-qwerty-devin-cli
```

Start a new session and ask *"show the SpinDoctor functions"*, or type `/spindoctor-qwerty:spindoctor-qwerty`.
`devin plugins remove spindoctor-qwerty` (add `--local` for a local install) removes it.

**Windows:** the python.org installer provides `python` and `py`, not `python3`. Use a local checkout and run
`python tools/set_python.py python` (or `py`, or a full path to `python.exe`) before `devin plugins install --local`. Running
`python3 tools/set_python.py python3` restores the original file byte for byte.

**Cloud sessions:** a plugin from your personal manifest also loads in Devin cloud sessions, where the MCP server runs on the cloud
machine (it needs Python 3.8+ there) and reports stay on that machine. Plugin subagents load only in the CLI and Devin Desktop.

## SpinDoctor Qwerty - plugin tools

| Function | What it does | Command to type |
|---|---|---|
| Function table (spindoctor_functions) | Show this table in chat | Ask: "show the SpinDoctor functions" or `/spindoctor-qwerty:spindoctor-qwerty show the functions` |
| Run a script (spindoctor_run_script) | Run any q.* lines above; returns results + TXT/JSON/CSV/PDF report paths | Ask: "run q.circuit new bell 2 / q.circuit add h 0 / ..." |
| Run a preset (spindoctor_run_preset) | Run qc-001..qc-241 with overrides | Ask: "run preset qc-067 with shots=64" |
| List presets (spindoctor_list_presets) | Search the 241 presets | Ask: "list presets about Grover" |
| Read a report (spindoctor_report) | List/read TXT reports (PDF/JSON paths alongside) | Ask: "show the newest SpinDoctor report" |
| Test a theory from a file (spindoctor_test_theory source=file) | Read a .txt/.md/.pdf/.py/.json/.csv/.q attachment, then hypothesis -> prediction -> q.* script -> run -> verdict + TXT/PDF theory report | Ask: "test the theory in C:/notes/theory.md" (the host must pass the file path/content) |
| Test a theory from text (spindoctor_test_theory source=text) | Same pipeline for pasted text | Ask: "test this theory: a Hadamard on \|0> gives 50/50" |
| Test the theory we discussed (spindoctor_test_theory source=chat) | The AI summarises the theory from the conversation (claims, assumptions, variables, prediction), you confirm, then it is tested; quoted excerpts go in the report under 'Source: chat history'. An exported chat transcript (.txt/.md/.json/.html) also works | Ask: "test the theory we discussed" or "test the theory in my exported chat C:/chats/conversation.json" |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)** (the exact table the tool shows):
circuits (`q.circuit`, including 298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register
(`q.tranche`), the procedural grid, presets and sequences, resource planning, math calculators, physics models, lessons, noise, error
correction, compilation, algorithms, inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

`spindoctor_test_theory` turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. In Devin, give the file's absolute path on your computer (or paste the text).
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The plugin cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `skills/spindoctor-qwerty/examples/theory/`. The two sample
PDFs are stored as text; run `python3 skills/spindoctor-qwerty/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Testing

| Test | Command | Result for 1.1.0 |
|---|---|---|
| Host check (real Devin CLI component checks + stand-in loader) | `DEVIN=$(command -v devin) python3 tests/devin_host_check.py` | 12/12 checks, end-to-end 12/12 |

**host-simulated.** The real Devin CLI (3000.6.11, the official binary from npm `@cognition-ai/cli-linux-x64`) was installed on a
Linux test machine without signing in. `devin plugins install --local` answers *"You must be logged in to manage plugins"*, and
sessions need a Devin account, so no plugin was installed in Devin and no session was started. No sign-in or API key was used.
Without signing in, the real CLI still loaded the plugin's parts when placed at project level: `devin skills list` listed the
skill, `devin rules list` listed the rule as agent-decidable, `devin doctor` loaded the subagent profile, and `devin mcp list/get`
read the server definition. `tests/devin_host_check.py` also validates `plugin.json` and `mcp.json` against the official Agent
Plugins 1.0.0 schemas, then stands in for Devin's plugin loader: it expands `${PLUGIN_ROOT}` and `${PLUGIN_DATA}`, starts the
server in the plugin folder and runs the full end-to-end suite through it. Whether Devin's agent picks the tools, rule and subagent
as intended isn't tested. Details in [E2E_RESULTS.md](E2E_RESULTS.md).

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). `plugin.json` carries the license and author. The Agent Plugins
schemas in `tests/schemas/` are Apache-2.0 (see NOTICE). Devin is a trademark of Cognition AI, Inc.; this project is not
affiliated with Cognition.
