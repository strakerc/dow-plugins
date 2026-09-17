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
        elif k in ("tags", "skills", "roles") and v:
            v = [t.strip() for t in v.split(",") if t.strip()]
        meta[k] = v
    return meta, m.group(2)


def parse_mock(path):
    meta, body = frontmatter(open(path, encoding="utf-8").read())
    return meta, body.strip("\n")


def visible(meta, role):
    """A mock with no `roles:` is every role's; `roles: lm` names the roles
    that can see it (frontmatter() already makes it a list; an unquoted
    `[lm, owner]` arrives as bracketed strings, stripped here)."""
    r = meta.get("roles")
    if not r:
        return True
    if isinstance(r, str):
        r = [r]
    return role in [str(x).strip().strip("[]").strip() for x in r]


def served_path(server, dirs, tool):
    """The file load_tools serves for `tool`: later dirs win, `_`-prefixed
    files are private. The one answer to "which mock does this case read",
    for the server and for the runner's fingerprint alike."""
    if tool.startswith("_"):
        return None
    found = None
    for d in dirs:
        cand = os.path.join(d, server, tool + ".md")
        if os.path.isfile(cand):
            found = cand
    return found


# The gateway's own argument schemas, copied from the live connector's tools/list
# on 14 Sep 2026 PT (dowgateway, the same surface the mock descriptions mirror).
# Until then every mock advertised an empty object, and sonnet at high effort
# answered that by wrapping every call as {"params": "<json string>"}: the
# server saw no `week`, rendered the season-long body, and the graders that
# match on the input JSON counted zero calls (lineup-two-tables, 14 Sep 2026
# PT). A tool with no entry here keeps the open schema. Pinned to a dowgateway
# version under `schemas` in validation/mock-mirrors.json (audit check 9).
SCHEMAS = {
 "get_projections": {
  "type": "object",
  "required": [
   "position",
   "week"
  ],
  "properties": {
   "full": {
    "description": "Untrimmed upstream payload. Defaults false. ALL untrimmed is ~240 KB.",
    "type": "boolean"
   },
   "position": {
    "description": "ALL returns every position in one call and is preferred for a lineup.",
    "enum": [
     "ALL",
     "QB",
     "RB",
     "WR",
     "TE",
     "K",
     "DST"
    ],
    "type": "string"
   },
   "week": {
    "description": "NFL week 1-18. Required; there is no default, on purpose.",
    "maximum": 18,
    "minimum": 1,
    "type": "integer"
   }
  }
 },
 "get_weekly_results": {
  "type": "object",
  "properties": {
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   },
   "week": {
    "type": "string"
   }
  }
 },
 "get_rosters": {
  "type": "object",
  "properties": {
   "franchise_id": {
    "description": "Optional 4-digit franchise id for one team.",
    "type": "string"
   },
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   }
  }
 },
 "get_matchups": {
  "type": "object",
  "properties": {
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   },
   "week": {
    "type": "string"
   }
  }
 },
 "get_nfl_schedule": {
  "type": "object",
  "properties": {
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   },
   "week": {
    "description": "Optional NFL week (1-18). Omit for the current week.",
    "type": "string"
   }
  }
 },
 "get_player_scores": {
  "type": "object",
  "properties": {
   "count": {
    "description": "Limit results, e.g. '50'.",
    "type": "string"
   },
   "players": {
    "description": "Comma-separated player ids.",
    "type": "string"
   },
   "position": {
    "enum": [
     "QB",
     "RB",
     "WR",
     "TE",
     "PK",
     "DEF"
    ],
    "type": "string"
   },
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   },
   "week": {
    "description": "1-21, or 'YTD' for totals, or 'AVG' for per-game.",
    "type": "string"
   }
  }
 },
 "get_players": {
  "type": "object",
  "properties": {
   "details": {
    "description": "Include age, height, weight, draft year, status.",
    "type": "boolean"
   },
   "players": {
    "description": "Comma-separated MFL player ids. Strongly recommended.",
    "type": "string"
   },
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   }
  }
 },
 "get_player_values": {
  "type": "object",
  "required": [
   "players"
  ],
  "properties": {
   "players": {
    "description": "Semicolon-separated names. 'First Last' or 'Last, First' both work.",
    "type": "string"
   }
  }
 },
 "get_free_agents": {
  "type": "object",
  "properties": {
   "position": {
    "enum": [
     "QB",
     "RB",
     "WR",
     "TE",
     "PK",
     "DEF"
    ],
    "type": "string"
   },
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   }
  }
 },
 "evaluate_trade": {
  "type": "object",
  "required": [
   "teamB"
  ],
  "properties": {
   "aGives": {
    "description": "What team A sends: player names and/or picks.",
    "items": {
     "type": "string"
    },
    "type": "array"
   },
   "bGives": {
    "description": "What team B sends.",
    "items": {
     "type": "string"
    },
    "type": "array"
   },
   "teamA": {
    "description": "Owner first name or 4-digit MFL franchise id. Defaults to your own team.",
    "type": "string"
   },
   "teamB": {
    "description": "The other side.",
    "type": "string"
   }
  }
 },
 "get_injuries": {
  "type": "object",
  "properties": {
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   },
   "week": {
    "type": "string"
   }
  }
 },
 "get_standings": {
  "type": "object",
  "properties": {
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   }
  }
 },
 "get_transactions": {
  "type": "object",
  "properties": {
   "days": {
    "description": "Lookback window in days.",
    "type": "string"
   },
   "franchise_id": {
    "type": "string"
   },
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   },
   "transaction_type": {
    "description": "Omit for all types — and omit it if you want auction prices.",
    "enum": [
     "TRADE",
     "WAIVER",
     "FREE_AGENT",
     "BBID_WAIVER",
     "IR",
     "TAXI"
    ],
    "type": "string"
   }
  }
 },
 "get_league": {
  "type": "object",
  "properties": {
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   }
  }
 },
 "get_salary_adjustments": {
  "type": "object",
  "properties": {
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   }
  }
 },
 "get_future_draft_picks": {
  "type": "object",
  "properties": {
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   }
  }
 },
 "get_draft_results": {
  "type": "object",
  "properties": {
   "season": {
    "description": "Optional four-digit season, e.g. '2023'. Defaults to the current season. Use for history — auction prices, past contracts, prior standings.",
    "type": "string"
   }
  }
 },
 "list_channels": {
  "type": "object",
  "required": [
   "guild_id"
  ],
  "properties": {
   "guild_id": {
    "description": "From list_guilds.",
    "type": "string"
   }
  }
 },
 "send_message": {
  "type": "object",
  "required": [
   "channel_id",
   "content"
  ],
  "properties": {
   "channel_id": {
    "description": "From list_channels.",
    "type": "string"
   },
   "content": {
    "description": "Message text to post.",
    "type": "string"
   }
  }
 },
 "get_dynasty_rankings": {
  "type": "object",
  "properties": {}
 },
 "get_rookie_rankings": {
  "type": "object",
  "properties": {}
 }
}


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
    ap.add_argument("--role", default="owner",
                    help="the caller's gateway role: a mock whose front matter says "
                         "`roles: lm` is served to lm only, the way dowgateway hides "
                         "LM_ONLY tools from an owner key (13 Sep 2026 PT)")
    a = ap.parse_args()
    tools = {n: t for n, t in load_tools(a.server, a.mocks).items() if visible(t[0], a.role)}

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
                 "inputSchema": SCHEMAS.get(n, {"type": "object", "properties": {},
                                              "additionalProperties": True})}
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
