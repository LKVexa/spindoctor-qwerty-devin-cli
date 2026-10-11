# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for Devin CLI
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Devin CLI host check. Standard library only (Python 3.8+). No account, no sign-in, no API key, no model.

1. Static: plugin.json and mcp.json validated against the official Agent Plugins 1.0.0 JSON schemas (tests/schemas,
   Apache-2.0) - the root-manifest layout Devin documents, where ${PLUGIN_ROOT}/${PLUGIN_DATA} are expanded; no
   .devin-plugin/ or .claude-plugin/ manifest (they would take precedence), no hooks.json, no AGENTS.md (always-on rule);
   rule `trigger` front matter, subagent and skill front matter; mcp.json uses only ${PLUGIN_ROOT}; text files only;
   tools/set_python.py round-trip.
2. REAL Devin CLI (DEVIN=/path/to/devin) in a throw-away HOME: `devin plugins install --local` needs a signed-in account (recorded
   as INFO). Without signing in, the real CLI still loads the plugin's components when they are placed at project level:
   `devin skills list` lists /spindoctor-qwerty, `devin rules list` lists the rule as agent-decidable, `devin doctor` loads the
   qwerty-helper subagent profile, and `devin mcp list` / `devin mcp get` read the server from .devin/mcp_config.json.
3. Stand-in loader (the documented Agent Plugins runtime conventions): read plugin.json + mcp.json, expand ${PLUGIN_ROOT} and
   ${PLUGIN_DATA}, pass PLUGIN_ROOT/PLUGIN_DATA in the environment, start the stdio server with the plugin root as cwd and run the
   full end-to-end suite (tests/e2e_mcp.py) through it.

usage: python3 tests/devin_host_check.py [REPO_DIR]"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT = (".py", ".md", ".json", ".txt", ".csv", ".html", ".q", "")
S10 = "https://agent-plugins.org/schemas/1.0.0/"


def validate(inst, schema, root=None, path="$"):
    """Small JSON Schema (2020-12) subset: everything the Agent Plugins schemas use."""
    root = root or schema; errs = []
    if "$ref" in schema:
        node = root
        for part in schema["$ref"].lstrip("#/").split("/"): node = node[part]
        return validate(inst, node, root, path)
    if "oneOf" in schema:
        n = sum(1 for s in schema["oneOf"] if not validate(inst, s, root, path))
        if n != 1: errs.append("%s: matches %d of oneOf" % (path, n))
    t = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "boolean": bool}
    if t and not isinstance(inst, types[t]): return errs + ["%s: not %s" % (path, t)]
    if "const" in schema and inst != schema["const"]: errs.append("%s: must be %r" % (path, schema["const"]))
    if isinstance(inst, str):
        if len(inst) < schema.get("minLength", 0) or len(inst) > schema.get("maxLength", 10 ** 9): errs.append(path + ": length")
        if "pattern" in schema and not re.search(schema["pattern"], inst): errs.append(path + ": pattern")
    if isinstance(inst, list) and "items" in schema:
        for i, v in enumerate(inst): errs += validate(v, schema["items"], root, "%s[%d]" % (path, i))
    if isinstance(inst, dict):
        props = schema.get("properties", {})
        errs += ["%s: missing %s" % (path, k) for k in schema.get("required", []) if k not in inst]
        for k, v in inst.items():
            if "propertyNames" in schema and k in schema["propertyNames"].get("not", {}).get("enum", []): errs.append("%s: name %s not allowed" % (path, k))
            if k in props: errs += validate(v, props[k], root, path + "." + k)
            elif schema.get("additionalProperties") is False: errs.append("%s: unknown field %s" % (path, k))
            elif isinstance(schema.get("additionalProperties"), dict): errs += validate(v, schema["additionalProperties"], root, path + "." + k)
    return errs


def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---\n", open(path, encoding="utf-8").read(), re.S)
    return dict(re.findall(r"^([A-Za-z_-]+):\s*(.+)$", m.group(1), re.M)) if m else {}


def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---\n", open(path, encoding="utf-8").read(), re.S)
    return dict(re.findall(r"^([A-Za-z_-]+):\s*(.+)$", m.group(1), re.M)) if m else {}


def main():
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"; sys.dont_write_bytecode = True
    repo = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
    ok = True; mode = "host-simulated"

    def T(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond); print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)[:700])); sys.stdout.flush()

    load = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))
    pj, mj = load(repo, "plugin.json"), load(repo, "mcp.json")
    sch = os.path.join(HERE, "schemas", "agent-plugins", "1.0.0")
    e = validate(pj, load(sch, "plugin.schema.json")) + validate(mj, load(sch, "mcp.schema.json"))
    T("plugin.json + mcp.json valid against the official Agent Plugins 1.0.0 schemas", not e, e)
    T("plugin.json: $schema 1.0.0, Devin name rule (lowercase, single - or . separators), version 1.1.0, author, GPL-3.0-or-later",
      pj["$schema"] == S10 + "plugin.schema.json" and re.match(r"^[a-z0-9]+([-.][a-z0-9]+)*$", pj["name"]) and pj["version"] == "1.1.0"
      and pj["author"]["name"] == "RUSSELL PHILIP SMITHSON" and pj["license"] == "GPL-3.0-or-later", pj)
    T("one manifest only (no .devin-plugin/ or .claude-plugin/, which Devin would prefer), no hooks.json, no AGENTS.md, no .mcp.json",
      not any(os.path.exists(os.path.join(repo, p)) for p in (".devin-plugin", ".claude-plugin", "hooks.json", "AGENTS.md", ".mcp.json")))
    s = mj["mcpServers"].get("spindoctor-qwerty", {}); blob = json.dumps(mj)
    T("mcp.json: one stdio server, python3 ${PLUGIN_ROOT}/skills/.../spindoctor_mcp.py, no other host variables, no secrets",
      list(mj["mcpServers"]) == ["spindoctor-qwerty"] and s.get("type") == "stdio" and s.get("command") == "python3"
      and s.get("args") == ["${PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py"]
      and not re.search(r"CLAUDE_|CURSOR_|EXTENSION_PATH|\$\{env:|secret|token|key", blob, re.I)
      and os.path.isfile(os.path.join(repo, "skills/spindoctor-qwerty/scripts/spindoctor_mcp.py")), mj)
    rf, af, sf = frontmatter(os.path.join(repo, "rules", "spindoctor-qwerty.md")), frontmatter(os.path.join(repo, "agents", "qwerty-helper.md")), frontmatter(os.path.join(repo, "skills", "spindoctor-qwerty", "SKILL.md"))
    alltext = "".join(open(os.path.join(r, f), encoding="utf-8").read() for d in ("rules", "agents", "skills") for r, _, fs in os.walk(os.path.join(repo, d)) for f in fs if f.endswith(".md"))
    T("front matter: rule trigger model_decision + description; subagent name/description; skill name/description; honest limits; absolute paths",
      rf.get("trigger") == "model_decision" and rf.get("description") and af.get("name") == "qwerty-helper" and af.get("description")
      and sf.get("name") == "spindoctor-qwerty" and sf.get("description") and "not a quantum computer" in alltext and "298" in alltext and "ABSOLUTE" in alltext
      and not re.search(r"Copilot|Cline|CodeBuddy|Cursor|\$ARGUMENTS", alltext), (rf, af, sf))
    bad = [os.path.relpath(os.path.join(r, f), repo) for r, ds, fs in os.walk(repo) if ".git" not in r.split(os.sep) and "__pycache__" not in r
           for f in fs if os.path.splitext(f)[1].lower() not in TEXT and not (f.endswith(".pdf") and r.endswith(os.path.join("examples", "theory")))]
    T("only text files (sample PDFs are generated by make_sample_pdfs.py and git-ignored)", not bad, bad)
    tmp = tempfile.mkdtemp(prefix="sdq_devin_")
    cp = os.path.join(tmp, "copy"); shutil.copytree(repo, cp, ignore=shutil.ignore_patterns(".git"))
    orig = open(os.path.join(cp, "mcp.json"), "rb").read()
    r1 = subprocess.run([sys.executable, os.path.join(cp, "tools", "set_python.py"), "python"], stdout=subprocess.PIPE, text=True)
    mid = json.load(open(os.path.join(cp, "mcp.json")))["mcpServers"]["spindoctor-qwerty"]["command"]
    r2 = subprocess.run([sys.executable, os.path.join(cp, "tools", "set_python.py"), "python3"], stdout=subprocess.PIPE, text=True)
    r3 = subprocess.run([sys.executable, os.path.join(cp, "tools", "set_python.py"), "py; rm -rf ~"], stdout=subprocess.PIPE, text=True)
    T("tools/set_python.py: python -> mcp.json command 'python'; python3 restores it byte for byte; shell metacharacters refused",
      r1.returncode == 0 and mid == "python" and r2.returncode == 0 and open(os.path.join(cp, "mcp.json"), "rb").read() == orig and r3.returncode == 2)

    devin = os.environ.get("DEVIN") or shutil.which("devin")
    if devin:
        home = os.path.join(tmp, "home"); proj = os.path.join(tmp, "project"); os.makedirs(home); os.makedirs(os.path.join(proj, ".devin"))
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": home, "XDG_CONFIG_HOME": os.path.join(home, ".config"),
               "XDG_DATA_HOME": os.path.join(home, ".local", "share"), "DBUS_SESSION_BUS_ADDRESS": "disabled:", "NO_COLOR": "1", "TERM": "dumb"}

        def run(*a):
            return subprocess.run([devin] + list(a), cwd=proj, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
        subprocess.run(["git", "init", "-q", proj])
        v = run("--version").stdout.strip()
        r = run("plugins", "install", "--local", "-y", repo)
        print("INFO real %s: `devin plugins install --local -y <repo>` answers: %s" % (v, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "(no output)"))
        for d in ("skills", "rules", "agents"):
            shutil.copytree(os.path.join(repo, d), os.path.join(proj, ".devin", d))
        srv = json.loads(json.dumps(s).replace("${PLUGIN_ROOT}", repo)); srv.pop("type", None)
        json.dump({"mcpServers": {"spindoctor-qwerty": srv}}, open(os.path.join(proj, ".devin", "mcp_config.json"), "w"), indent=2)
        sk, ru, doc = run("skills", "list").stdout, run("rules", "list").stdout, run("doctor").stdout
        T("real %s (no sign-in), components at project level: skills list shows /spindoctor-qwerty with its description" % v,
          re.search(r"/spindoctor-qwerty \[[^\]]*model[^\]]*\] \(\./\.devin/skills/spindoctor-qwerty\) - Run the SpinDoctor 3\.1\.2", sk), sk[-600:])
        T("real devin: rules list shows spindoctor-qwerty as agent-decidable (trigger model_decision)", re.search(r"spindoctor-qwerty .*agent-decidable", ru), ru[-400:])
        T("real devin: doctor loads the qwerty-helper custom subagent profile with no failures", re.search(r"pass\s+custom subagent profiles.*qwerty-helper", doc)
          and " 0 failure(s)" in doc, doc[-500:])
        ml, mg = run("mcp", "list").stdout, run("mcp", "get", "spindoctor-qwerty").stdout
        T("real devin: mcp list/get read the server definition (stdio, python3, the plugin's spindoctor_mcp.py)",
          "spindoctor-qwerty" in ml and "python3" in mg and "spindoctor_mcp.py" in mg, (ml[-300:], mg[-400:]))
    else:
        print("SKIP real Devin CLI not found (set DEVIN=/path/to/devin)")

    data = os.path.join(tmp, "plugin-data", "spindoctor-qwerty"); os.makedirs(data)
    srv = json.loads(json.dumps(s).replace("${PLUGIN_ROOT}", repo).replace("${PLUGIN_DATA}", data))
    env2 = dict(os.environ, **srv.get("env", {}), PLUGIN_ROOT=repo, PLUGIN_DATA=data, SPINDOCTOR_WORKSPACE=os.path.join(tmp, "ws"), HOME=os.path.join(tmp, "home2"))
    os.makedirs(env2["HOME"], exist_ok=True)
    cmd = shutil.which(srv["command"]) or sys.executable
    r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server", cmd] + srv["args"]
                       + ["--examples", os.path.join(repo, "skills", "spindoctor-qwerty", "examples", "theory"), "--out", os.path.join(tmp, "e2e_results.json")],
                       cwd=repo, env=env2)
    T("stand-in loader: ${PLUGIN_ROOT}/${PLUGIN_DATA} expanded, PLUGIN_ROOT/PLUGIN_DATA in env, cwd = plugin root; end-to-end through the MCP server", r.returncode == 0)
    shutil.rmtree(tmp, ignore_errors=True)
    print("HOST-CHECK (host-simulated: Devin stand-in loader + real Devin CLI component checks)", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
