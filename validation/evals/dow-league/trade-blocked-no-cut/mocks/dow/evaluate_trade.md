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
   },
   {
    "kind": "player",
    "id": "10012",
    "label": "Ansel Okafor",
    "position": "RB",
    "nflTeam": "GB",
    "marketValue": 300,
    "salary": 5,
    "contract": "Free Agent",
    "contractThrough": "2026",
    "rosterStatus": "ROSTER",
    "surplus": -8,
    "annual": -40,
    "termFactor": 0.2,
    "escapable": true,
    "currentYearWeight": 0.2,
    "news": {
     "links": {
      "mfl": "https://mfl.example.org/2026/player?L=1&P=10012"
     }
    }
   },
   {
    "kind": "player",
    "id": "10013",
    "label": "Dmitri Sol",
    "position": "QB",
    "nflTeam": "SEA",
    "marketValue": 150,
    "salary": 3,
    "contract": "Free Agent",
    "contractThrough": "2026",
    "rosterStatus": "ROSTER",
    "surplus": -6,
    "annual": -30,
    "termFactor": 0.2,
    "escapable": true,
    "currentYearWeight": 0.2,
    "news": {
     "links": {
      "mfl": "https://mfl.example.org/2026/player?L=1&P=10013"
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
   }
  ]
 },
 "market": {
  "valueMovedA": 2150,
  "valueMovedB": 1200,
  "edgeVsValueMovedPct": 28,
  "verdict": "clear edge to Bram on market value"
 },
 "leagueAdjusted": {
  "surplusA": -86,
  "surplusB": 612,
  "edgeVsValueMovedPct": 21,
  "verdict": "edge to Ada"
 },
 "divergence": "Market favours Bram, but the contracts favour Ada: Milo Grant is signed through 2027 at $12 against a market value well above that price, while the three players going to Bram are at or below market for their salaries.",
 "legality": {
  "teamA": {
   "ok": true,
   "capSpaceAfter": 31.0,
   "activeAfter": 11
  },
  "teamB": {
   "ok": false,
   "blocked": true,
   "capSpaceAfter": -11.0,
   "activeAfter": 17,
   "problems": [
    "Bram is $11 over the $375 cap after this trade"
   ],
   "reason": "Bram is $11 over the $375 cap after this trade"
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
