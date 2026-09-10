---
description: Score a proposed trade: market verdict and league-adjusted verdict, divergence sentence, legality. teamA defaults to the caller's team. Raw payload for the dow-league skills, not an answer for an owner. Invoke the `league-trade-evaluator` skill BEFORE calling this; it explains the market and league-adjusted verdicts in an owner's words. Synthetic.
---
{
 "ok": true,
 "teamA": {
  "owner": "Ada",
  "gives": [
   "Felix Marsh"
  ]
 },
 "teamB": {
  "owner": "Bram",
  "gives": [
   "Milo Grant"
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
 "priceCurve": {
  "sampleSize": 180,
  "basis": "league-wide rosters"
 },
 "notes": []
}
