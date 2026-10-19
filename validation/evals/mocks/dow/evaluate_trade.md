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
    "id": "10007",
    "label": "Felix Marsh",
    "position": "WR",
    "nflTeam": "SEA",
    "marketValue": 1700,
    "salary": 14,
    "contract": "Long-Term",
    "contractThrough": "2027",
    "rosterStatus": "ROSTER",
    "news": {
     "links": {
      "mfl": "https://mfl.example.org/2026/player?L=1&P=10007",
      "rotowire": "https://rotowire.example.org/football/player/felix-marsh-20007",
      "espn": "https://espn.example.org/nfl/player/_/id/30007/felix-marsh"
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
    "id": "10031",
    "label": "Milo Grant",
    "position": "RB",
    "nflTeam": "PIT",
    "marketValue": 1200,
    "salary": 12,
    "contract": "Long-Term",
    "contractThrough": "2027",
    "rosterStatus": "ROSTER",
    "news": {
     "links": {
      "mfl": "https://mfl.example.org/2026/player?L=1&P=10031"
     }
    }
   }
  ]
 },
 "market": {
  "valueMovedA": 1700,
  "valueMovedB": 1200,
  "edgeVsValueMovedPct": 12,
  "verdict": "slight edge to Bram on market value"
 },
 "leagueAdjusted": {
  "surplusA": -420,
  "surplusB": 610,
  "edgeVsValueMovedPct": 57,
  "verdict": "clear win Ada"
 },
 "divergence": "Market calls this close, but the contracts favour Ada: Milo Grant is signed through 2027 at $12 against a market value that puts him around the 80th most valuable player, while Felix Marsh's $14 through 2027 is roughly at market.",
 "legality": {
  "teamA": {
   "ok": true,
   "capSpaceAfter": 21.0,
   "activeAfter": 13
  },
  "teamB": {
   "ok": false,
   "blocked": true,
   "reason": "Bram would be $3 over the cap after the trade"
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
