# Dynasty of Whiners — league tools

Eleven skills, all computing from live MyFantasyLeague data on every run. Nothing
here hardcodes last year's numbers, so any two owners asking the same question
get the same answer and can compare working.

| Skill | Ask it |
|---|---|
| `league-rules` | "can I do this", "what does that cost", "is he IR eligible" |
| `league-contracts` | "what are my options on X", "how much dead money if I cut" |
| `league-draft-picks` | "what picks do I have", "who owns my 2028 1st" |
| `league-franchise-tags` | "what would it cost to tag him" |
| `league-matchups` | "who do I play in week 6", "what tier am I in and why" |
| `league-contacts` | "what's Zef's number", "how do I reach Pat", "everyone's contact details" |
| `league-trade-evaluator` | "is this trade fair", "who wins this deal" |
| `league-player-values` | "what's X worth", "is he overpaid", "who's the better asset" |
| `league-trade-history` | "how did that trade turn out", "who won the Worthy trade" |
| `league-lineup` | "set my lineup", "who should I start", "start or sit week 6" |
| `league-player-status` | "who has X", "is he available", "how serious is his injury", "with X on IR, who should I target" |

## Setup — one paste, on a personal account

The skills reach MFL through a gateway that issues one key per owner. After
installing this plugin, add the connector URL Straker sent you at
**claude.ai → Customize → Connectors**. The plugin itself carries no key.

**Do this on a personal Claude account.** Team and Enterprise members cannot add
their own connectors — an admin has to — so on a work account the option is
simply missing, which looks like the plugin is broken when it isn't.

## What your key can reach

Your key decides which tools answer. Members get the fifteen-odd read tools these
skills need. A tool your role cannot use reports as `Unknown tool` rather than a
permissions error, so if a skill says it doesn't have a tool it should have,
that is a key problem — tell Straker rather than debugging the skill.

## The one thing worth knowing

**Schedules are read here, never generated.** The schedule in MFL is the one the
league plays. `league-matchups` reports it and will say so if MFL has none
loaded yet.
