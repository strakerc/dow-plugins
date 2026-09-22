---
description: "NFL schedule for a week: every game with `kickoff` in Unix seconds (convert to Pacific and label the zone), `gameSecondsRemaining` (3600 = not started, 0 = final), each side's `id` (MFL team code, the same code as `team` on a roster row), `isHome`, `score` and `spread`. Each side also carries `passDefenseRank`, `rushDefenseRank`, `passOffenseRank` and `rushOffenseRank`: 1 is the best unit, so a HIGH defence rank is a soft matchup; blank before the season has data. Omit `week` for the current week. This is the only kickoff source in the stack: a lock time not read from here is a guess. Raw payload for the dow-league skills, not an answer for an owner. Invoke the `league-lineup` skill BEFORE calling this. Synthetic: week 3 (kickoffs 16-20 Sep 2027 PT, moved forward a year on 21 Sep 2026 PT because the real week-3 dates had passed while every game still read unstarted, and sonnet at high effort refused to state a lock time it could not reconcile; same weekdays and clock times), the twelve NFL teams the synthetic league rosters, Thursday and Monday games included; every game unstarted; unit ranks out of 32."
---
{
 "version": "1.0",
 "encoding": "utf-8",
 "nflSchedule": {
  "matchup": [
   {
    "kickoff": "1821140100",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "DAL",
      "isHome": "0",
      "score": "",
      "spread": "3.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "11",
      "rushOffenseRank": "20",
      "passDefenseRank": "14",
      "rushDefenseRank": "19"
     },
     {
      "id": "GB",
      "isHome": "1",
      "score": "",
      "spread": "-3.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "9",
      "rushOffenseRank": "22",
      "passDefenseRank": "12",
      "rushDefenseRank": "11"
     }
    ]
   },
   {
    "kickoff": "1821373200",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "SEA",
      "isHome": "0",
      "score": "",
      "spread": "-1.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "17",
      "rushOffenseRank": "9",
      "passDefenseRank": "13",
      "rushDefenseRank": "10"
     },
     {
      "id": "PIT",
      "isHome": "1",
      "score": "",
      "spread": "1.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "24",
      "rushOffenseRank": "21",
      "passDefenseRank": "31",
      "rushDefenseRank": "18"
     }
    ]
   },
   {
    "kickoff": "1821373200",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "BUF",
      "isHome": "0",
      "score": "",
      "spread": "2.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "4",
      "rushOffenseRank": "6",
      "passDefenseRank": "20",
      "rushDefenseRank": "13"
     },
     {
      "id": "DET",
      "isHome": "1",
      "score": "",
      "spread": "-2.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "7",
      "rushOffenseRank": "12",
      "passDefenseRank": "21",
      "rushDefenseRank": "16"
     }
    ]
   },
   {
    "kickoff": "1821384300",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "MIA",
      "isHome": "0",
      "score": "",
      "spread": "4.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "21",
      "rushOffenseRank": "18",
      "passDefenseRank": "15",
      "rushDefenseRank": "19"
     },
     {
      "id": "LAR",
      "isHome": "1",
      "score": "",
      "spread": "-4.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "16",
      "rushOffenseRank": "13",
      "passDefenseRank": "17",
      "rushDefenseRank": "22"
     }
    ]
   },
   {
    "kickoff": "1821385500",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "DEN",
      "isHome": "0",
      "score": "",
      "spread": "6.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "18",
      "rushOffenseRank": "19",
      "passDefenseRank": "11",
      "rushDefenseRank": "21"
     },
     {
      "id": "KC",
      "isHome": "1",
      "score": "",
      "spread": "-6.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "5",
      "rushOffenseRank": "10",
      "passDefenseRank": "2",
      "rushDefenseRank": "11"
     }
    ]
   },
   {
    "kickoff": "1821485700",
    "gameSecondsRemaining": "3600",
    "team": [
     {
      "id": "PHI",
      "isHome": "0",
      "score": "",
      "spread": "-2.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "12",
      "rushOffenseRank": "14",
      "passDefenseRank": "16",
      "rushDefenseRank": "15"
     },
     {
      "id": "SF",
      "isHome": "1",
      "score": "",
      "spread": "2.5",
      "hasPossession": "0",
      "inRedZone": "0",
      "passOffenseRank": "8",
      "rushOffenseRank": "11",
      "passDefenseRank": "18",
      "rushDefenseRank": "14"
     }
    ]
   }
  ]
 }
}
