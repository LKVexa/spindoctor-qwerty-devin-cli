---
trigger: model_decision
description: Apply when the user asks for quantum circuits, SpinDoctor presets, q.* scripts, q.folder jobs, theory tests or SpinDoctor reports, and whenever presenting SpinDoctor simulator results.
---

# SpinDoctor Qwerty 1.1.0 (Devin CLI plugin) - SpinDoctor 3.1.2 quantum-circuit simulator

Use the `spindoctor_*` tools when the user wants to build, run or explain quantum circuits, run a SpinDoctor preset
(qc-001 ... qc-241), run a folder of command files, test a theory, or get a TXT/PDF report of a simulation.

**Honesty rules (always follow):** SpinDoctor is a classical FP64 simulator running on this computer. It is not a
quantum computer and gives no quantum speed-up or advantage. Registers hold 1-298 logical qubits, but one entangled
group (factor) is limited to 59 qubits and dense factors are limited by memory (2^n x 16 bytes). Registers wider than
29 qubits sample in basis Z only. Histograms come from seeded Born sampling, so counts fluctuate around the exact
probabilities. Never describe results as coming from quantum hardware or as a quantum advantage.

**Tools:** `spindoctor_run_script` (q.* commands, one per line), `spindoctor_run_preset`, `spindoctor_list_presets`,
`spindoctor_report`, `spindoctor_functions` and `spindoctor_test_theory`. Every command writes TXT, JSON, PDF (and CSV where
tabular) reports into the workspace (default `~/spindoctor-workspace`, or `$SPINDOCTOR_WORKSPACE`). The MCP server runs with the
plugin folder as its working directory, so always pass ABSOLUTE paths for files and folders.

## Command grammar (most used)

- `q.circuit new NAME QUBITS` (1..298) - `q.circuit add GATE [angles...] QUBITS|all` - gates include h x y z s sdg t tdg
  sx rx ry rz p u cx cy cz ch swap cp crx cry crz ccx cswap and `mcx7` (controls 0..6 of the operands, target last).
- `q.circuit run shots N basis z|x|y` then `q.circuit result` / `q.circuit status`; `q.query ...` on the last run.
- `q.folder run path="FOLDER"` runs every .txt/.csv/.json/.qasm/.qasm2/.circuit/.pdf file at the top level of a folder
  (1-128 files, 4 MiB each, 1-128 commands per file, 4096 characters per command, strict UTF-8; other files are skipped
  and listed; the first failing file stops the job).
- Calculators `q.math`, `q.resource`, `q.model`, `q.lesson`, `q.noise`, `q.qec`, `q.compile`, `q.algorithm`;
  tranche register `q.tranche`; procedural grid `q.prepare/q.gate/q.measure`; `q.preset list|show|run`; `q.help`.

## Function table (show it in chat)

On first use, and whenever the user asks what SpinDoctor can do, asks for help, "functions", "commands" or a "menu",
call `spindoctor_functions` and show the returned Markdown table **verbatim** (Function | What it does | Command to
type). `section="presets"` lists the 241 presets; `filter="noise"` narrows it.

## Testing a theory (file, pasted text, or the chat itself)

1. **Get the theory.** File (txt, md, pdf, py, json, csv or q.* script): `source="file"`, `path=...`,
   `action="extract"`. Pasted text: `source="text"`. **From the chat history** ("test the theory we discussed"):
   gather the theory from the conversation you can see and write a short summary - claims, assumptions, variables,
   measurable prediction. **Show it to the user and ask them to confirm or correct it before running.** Then call with
   `source="chat"`, `text=<confirmed summary>` and `excerpts=[...]` (short verbatim quotes "User: ...", "Assistant: ...").
   An exported chat transcript (.txt/.md/.json/.html) can be passed as `path`. The plugin cannot read the chat by
   itself, and very long chats may already be cut off by the host's context window - say so if that may matter.
2. **Restate the hypothesis** and a **measurable prediction**.
3. **Write a q.* script** and machine `checks`, e.g. `{"kind":"probability","outcome":"11","expected":0.5,"tolerance":0.05}`
   (bitstrings put qubit 0 on the RIGHT) or `{"kind":"value","command":5,"path":"result.fidelity","op":"approx","value":1,"tolerance":1e-9}`.
4. **Run** with `action="run"`; each run uses a fresh sub-workspace.
5. **Report**: verdict (supported / not supported / inconclusive), observed vs predicted numbers, and the TXT + PDF
   theory report paths. Repeat the limits: classical simulation of an idealised model, shot noise, qubit limits.

**Attachments in Devin:** give the file's absolute path on this computer (or paste the text); the tools read local paths only.

`q.compile synthesize` is not implemented in SpinDoctor 3.1.2 either (it returns an explanatory error).
