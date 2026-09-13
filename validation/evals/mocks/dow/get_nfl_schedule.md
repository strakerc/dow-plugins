---
description: NFL schedule for a week: every game with `kickoff` in Unix seconds (convert to Pacific and label the zone), `gameSecondsRemaining` (3600 = not started, 0 = final), each side's `id` (MFL team code, the same code as `team` on a roster row), `isHome`, `score` and `spread`. Omit `week` for the current week. This is the only kickoff source in the stack: a lock time not read from here is a guess. Raw payload for the dow-league skills, not an answer for an owner. Invoke the `league-lineup` skill BEFORE calling this. Synthetic: week 3 of 2026, the twelve NFL teams the synthetic league rosters, Thursday and Monday games included; every game unstarted.
---
{
 "version": "1.0",
 "encoding": "utf-8",
 "nflSchedule": {
  "matchup": [
   {
    "kickoff": "1789690500",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "DAL",
      "isHome": "0",
      "score": "",
      "spread": "3.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     },
     {
      "id": "GB",
      "isHome": "1",
      "score": "",
      "spread": "-3.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     }
    ]
   },
   {
    "kickoff": "1789923600",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "SEA",
      "isHome": "0",
      "score": "",
      "spread": "-1.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     },
     {
      "id": "PIT",
      "isHome": "1",
      "score": "",
      "spread": "1.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     }
    ]
   },
   {
    "kickoff": "1789923600",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "BUF",
      "isHome": "0",
      "score": "",
      "spread": "2.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     },
     {
      "id": "DET",
      "isHome": "1",
      "score": "",
      "spread": "-2.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     }
    ]
   },
   {
    "kickoff": "1789934700",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "MIA",
      "isHome": "0",
      "score": "",
      "spread": "4.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     },
     {
      "id": "LAR",
      "isHome": "1",
      "score": "",
      "spread": "-4.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     }
    ]
   },
   {
    "kickoff": "1789935900",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "DEN",
      "isHome": "0",
      "score": "",
      "spread": "6.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     },
     {
      "id": "KC",
      "isHome": "1",
      "score": "",
      "spread": "-6.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     }
    ]
   },
   {
    "kickoff": "1790036100",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "PHI",
      "isHome": "0",
      "score": "",
      "spread": "-2.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     },
     {
      "id": "SF",
      "isHome": "1",
      "score": "",
      "spread": "2.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "",
      "rushOffenseRank": "",
      "passDefenseRank": "",
      "rushDefenseRank": ""
     }
    ]
   }
  ]
 }
}
