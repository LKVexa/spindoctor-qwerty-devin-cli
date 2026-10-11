# Changelog

## 1.1.0 - 2026-10-11

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics (.qasm2/.circuit, skipped-file listing, compact status, 128 files /
  4 MiB / 128 commands / 4096 characters), CSV report copies and measurement-CSV fitting equations. All 241 presets replayed.
- New tools `spindoctor_functions` (in-chat function table) and `spindoctor_test_theory` (theory testing from a file, pasted text or
  the chat history, with TXT+JSON+PDF theory reports).
- Layout changed to Agent Plugins 1.0.0 (root `plugin.json` + `mcp.json` with `${PLUGIN_ROOT}`): the Devin docs document root-path
  expansion only for this layout and the Claude layout, not for `.devin-plugin/` with `${CLAUDE_PLUGIN_ROOT}` as 1.0 used. The
  repo root is now the plugin, so `devin plugins install LKVexa/spindoctor-qwerty-devin-cli` works.
- Removed the empty `hooks.json` (plugin hooks are best effort; nothing to run). Still no `AGENTS.md`.
- Rule renamed to `rules/spindoctor-qwerty.md` and extended (q.* grammar, function table, theory-testing steps, absolute paths);
  skill, subagent and rule updated for 3.1.2 (298-qubit limits, q.folder, theory testing with user confirmation).
- New `tools/set_python.py` for Windows (edits only `mcp.json`, refuses shell metacharacters, restores byte for byte).
- Tests: Devin host check (official Agent Plugins 1.0.0 schemas, real Devin CLI component loading, stand-in loader end-to-end).
- License changed from MIT to GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `spindoctor-qwerty/` folder with `.devin-plugin/plugin.json`, skill, rule, subagent, empty `hooks.json`, `.mcp.json`.
