# Dynasty of Whiners — Claude plugins

Two Cowork plugins for a 12-team dynasty fantasy football league
(MyFantasyLeague `29557`). This repository is the **marketplace**: add it in
Claude and both plugins appear, with updates pulled from here.

## Install

**Customize → Plugins → Add marketplace**, paste this repository's URL, then
install:

| Plugin | Who | What |
|---|---|---|
| **`dow-league`** | everyone | Rules lookup, contract decisions, draft pick ownership, franchise tag pricing, schedule lookup |
| **`dow-league-lm`** | league managers only | Schedule generation, rookie draft grades, FA auction writeup. **Requires `dow-league`** |

Then add your personal connector URL at **claude.ai → Customize → Connectors**.
Ask Straker for yours.

Use a **personal** Claude account. Team and Enterprise members cannot add their
own connectors — the option simply will not appear.

## This repository is public, and contains no secrets

The plugins ship skills and scripts. **No credentials, no API keys, no MCP
server definitions, no member contact details.** Every piece of league data
comes from a connector that each person adds to their own account with their own
key, and no key is in here.

Installing these plugins without a key gets you skills that have no tools to
call. They will say so.

> **Rule for anyone editing this repo: never add a `.mcp.json`.** A plugin can
> declare its own connector, and if one did, the URL — key and all — would be
> published here. The packaging check enforces zero.

## Layout

```
.claude-plugin/marketplace.json    the marketplace manifest
plugins/dow-league/                member package
plugins/dow-league-lm/             LM package
```

Each plugin has `.claude-plugin/plugin.json` and a `skills/` directory; skills
that need one carry a `scripts/` folder beside their `SKILL.md`.

## A convention that looks like a typo and is not

Dollar amounts under ten are written **without** the dollar sign — `+5`, not
`+$5` — and money tables put the unit in the column header. A dollar sign
followed by a single digit gets substituted at load time with a word from the
invocation arguments, silently, which once rewrote an entire rookie salary
scale into prose. Each affected skill carries an editing note. Please don't
"fix" it.
