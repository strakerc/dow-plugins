---
description: Score a proposed trade: market verdict and league-adjusted verdict, divergence sentence, legality. teamA defaults to the caller's team. Every player asset carries `news.links` (his MFL player page, and his Rotowire and ESPN pages when MFL holds those ids), and `notes` carries the one instruction for them: open each BEFORE advising, because every value here was pulled without any news. Follow that note as written; never build a link that is not in the payload. Raw payload for the dow-league skills, not an answer for an owner. Invoke the `league-trade-evaluator` skill BEFORE calling this; it explains the market and league-adjusted verdicts in an owner's words. Synthetic.
---
{
 "ok": true,
 "teamA": {
  "owner": "Ada",
  "gives": [
   {
    "kind": "player",
    "id": "10009",
    "label": "Felix Marsh",
    "position": "WR",
    "nflTeam": "MIA",
    "marketValue": 1700,
    "salary": 14,
    "contract": "Long-Term",
    "contractThrough": "2027",
    "rosterStatus": "ROSTER",
    "surplus": -72,
    "annual": -60,
    "termFactor": 1.2,
    "escapable": false,
    "currentYearWeight": 0.2,
    "news": {
     "links": {
      "mfl": "https://mfl.example.org/2026/player?L=1&P=10009"
     }
    }
   }
  ]
 },
 "teamB": {
  "owner": "Bram",
  "gives": [
   {
    "kind": "player",
    "id": "20006",
    "label": "Milo Grant",
    "position": "RB",
    "nflTeam": "MIA",
    "marketValue": 1200,
    "salary": 12,
    "contract": "Long-Term",
    "contractThrough": "2027",
    "rosterStatus": "ROSTER",
    "surplus": 612,
    "annual": 340,
    "termFactor": 1.8,
    "escapable": false,
    "currentYearWeight": 0.2,
    "news": {
     "links": {
      "mfl": "https://mfl.example.org/2026/player?L=1&P=20006"
     }
    }
   },
   {
    "kind": "player",
    "id": "20009",
    "label": "Ash Reilly",
    "position": "WR",
    "nflTeam": "GB",
    "marketValue": 350,
    "salary": 5,
    "contract": "Free Agent",
    "contractThrough": "2026",
    "rosterStatus": "ROSTER",
    "surplus": 10,
    "annual": 10,
    "termFactor": 1.0,
    "escapable": true,
    "currentYearWeight": 0.2,
    "news": {
     "links": {
      "mfl": "https://mfl.example.org/2026/player?L=1&P=20009"
     }
    }
   }
  ]
 },
 "market": {
  "valueMovedA": 1700,
  "valueMovedB": 1550,
  "edgeVsValueMovedPct": 4,
  "verdict": "even on market value"
 },
 "leagueAdjusted": {
  "surplusA": -72,
  "surplusB": 622,
  "edgeVsValueMovedPct": 19,
  "verdict": "edge to Ada"
 },
 "divergence": "A public trade calculator would call this even. It is not: Milo Grant's $12 through 2027 is well under his market value, and no external board prices contracts.",
 "legality": {
  "teamA": {
   "ok": true,
   "capSpaceAfter": 16.0,
   "activeAfter": 14
  },
  "teamB": {
   "ok": true,
   "capSpaceAfter": 2.0,
   "activeAfter": 16
  }
 },
 "capDollars": {
  "phase": "in-season",
  "currentYearDragWeight": 0.2,
  "note": "The season has started: an overpay on this year's salary counts at the weight shown, because a cap dollar cannot be redeployed until the August auction. Every future locked year counts in full."
 },
 "priceCurve": {
  "sampleSize": 180,
  "basis": "league-wide rosters"
 },
 "notes": [
  "FantasyPros returned only 426 players — expected at least 500. A player missing from its board is priced on FantasyCalc alone, so the blend is thinner than usual.",
  "Every player asset carries news.links. Open each link given and quote the newest dated item on that page, with its date, before advising: every value in this evaluation was pulled without it. A page that shows nothing new is worth saying so. A link that does not open, or opens to something that is not that player's page, is a failed check, not 'nothing new': say which, and search for dated news on him instead."
 ]
}
