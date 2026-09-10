#!/usr/bin/env python3
"""A stand-in for the league gateway: an MCP server over stdio that answers
every tool call from a canned file.

    python3 mock_mcp_server.py --server dow --mocks <dir> [<dir> ...]

It exists so a skill can be exercised end to end -- prompt in, tool calls out,
answer back -- without a key, without the network, and without a byte of real
league data. Straker's connector is never involved: the eval runner starts
Claude with `--strict-mcp-config`, so this is the ONLY server it can see.

MOCK FILES

    <dir>/<server>/<tool>.md

    ---
    description: one line, shown to the model as the tool's description
    ---
    {"rosters": {"franchise": [...]}}

The body is returned verbatim as the tool's text result. `{{input.week}}`
anywhere in the body is replaced with that argument from the call, so a mock
can echo what it was asked for (league-lineup asserts the echoed week matches).
Later --mocks directories override earlier ones file by file, which is how a
case overrides one tool of the shared set.

This mirrors the layout `claude plugin eval` documents for its own mocks
(<eval dir>/mocks/<server>/<tool>.md), so the same files serve both runners.

A tool with no file reports "Unknown tool", the way the real gateway does for a
tool the key cannot reach -- the skills are written to read that as a key
problem, and an eval can check they do.

No dependencies: raw JSON-RPC 2.0, one message per line, nothing else on
stdout. Every fixture under validation/evals is synthetic -- see the README.
"""
import argparse, json, os, re, sys

PROTOCOL = "2024-11-05"


def frontmatter(text):
    """The ONE front-matter reader for everything under validation/: mocks,
    case prompts, graders, and audit.py's coverage check all go through here,
    so they cannot disagree about a file. `key: value` lines between `---`
    fences; JSON lists/objects, true/false, integers and quoted strings are
    coerced; an unbracketed comma list (`skills: a, b`) becomes a list.
    Returns (meta, body)."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v.startswith("[") or v.startswith("{"):
            try:
                v = json.loads(v)
            except Exception:
                # Single quotes or a stray comma: a list that will not parse is
                # kept as text, and every consumer then sees a string where it
                # expected a list, which is the loud failure wanted here.
                pass
        elif v.lower() in ("true", "false"):
            v = v.lower() == "true"
        elif re.fullmatch(r"-?\d+", v):
            v = int(v)
        elif len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            v = v[1:-1]
        elif k in ("tags", "skills") and v:
            v = [t.strip() for t in v.split(",") if t.strip()]
        meta[k] = v
    return meta, m.group(2)


def parse_mock(path):
    meta, body = frontmatter(open(path, encoding="utf-8").read())
    return meta, body.strip("\n")


def load_tools(server, dirs):
    tools = {}
    for d in dirs:
        sub = os.path.join(d, server)
        if not os.path.isdir(sub):
            continue
        for fn in sorted(os.listdir(sub)):
            if fn.endswith(".md") and not fn.startswith("_"):
                tools[fn[:-3]] = parse_mock(os.path.join(sub, fn))
    return tools


def render(body, arguments):
    def sub(m):
        v = arguments.get(m.group(1))
        return "" if v is None else str(v)
    return re.sub(r"\{\{\s*input\.([A-Za-z0-9_]+)\s*\}\}", sub, body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", required=True)
    ap.add_argument("--mocks", nargs="+", required=True)
    a = ap.parse_args()
    tools = load_tools(a.server, a.mocks)

    out = sys.stdout.buffer
    def send(msg):
        out.write((json.dumps(msg) + "\n").encode("utf-8"))
        out.flush()

    for raw in sys.stdin.buffer:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw.decode("utf-8"))
        except Exception:
            continue
        rid, method, params = req.get("id"), req.get("method"), req.get("params") or {}
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": params.get("protocolVersion") or PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": f"mock-{a.server}", "version": "0.1"}}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": rid, "result": {"tools": [
                {"name": n, "description": meta.get("description", f"{n} (mock)"),
                 "inputSchema": {"type": "object", "properties": {},
                                 "additionalProperties": True}}
                for n, (meta, _) in tools.items()]}})
        elif method == "tools/call":
            name, args = params.get("name"), params.get("arguments") or {}
            if name in tools:
                send({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": render(tools[name][1], args)}],
                    "isError": False}})
            else:
                send({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                    "isError": True}})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": rid, "result": {}})
        elif rid is not None:
            send({"jsonrpc": "2.0", "id": rid,
                  "error": {"code": -32601, "message": f"method not found: {method}"}})


if __name__ == "__main__":
    main()
