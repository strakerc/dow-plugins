---
description: Head-to-head results for a week: every franchise's submitted lineup (`starters` and `nonstarters`, player ids with a trailing comma) and individual scores. Lineups are visible league-wide in this league, so before kickoff this is how to read what an owner or their opponent has submitted; a franchise with no `starters` has not submitted one yet. Raw payload for the dow-league skills, not an answer for an owner. Invoke the `league-lineup` skill BEFORE calling this for a lineup question, or `league-schedule` (LM) for prior-season results. Synthetic.
---
{
 "weeklyResults": {
  "week": "{{input.week}}",
  "matchup": [
   {
    "franchise": [
     {
      "id": "0001",
      "score": "",
      "starters": "10001,10007,10002,10008,10012,10003,10009,10014,10011,20005,",
      "nonstarters": "10010,10013,10015,",
      "player": [
       {"id": "10001", "status": "starter"},
       {"id": "10007", "status": "starter"},
       {"id": "10002", "status": "starter"},
       {"id": "10008", "status": "starter"},
       {"id": "10012", "status": "starter"},
       {"id": "10003", "status": "starter"},
       {"id": "10009", "status": "starter"},
       {"id": "10014", "status": "starter"},
       {"id": "10011", "status": "starter"},
       {"id": "20005", "status": "starter"},
       {"id": "10010", "status": "nonstarter"},
       {"id": "10013", "status": "nonstarter"},
       {"id": "10015", "status": "nonstarter"}
      ]
     },
     {
      "id": "0002",
      "score": ""
     }
    ]
   },
   {
    "franchise": [
     {
      "id": "0003",
      "score": ""
     },
     {
      "id": "0012",
      "score": ""
     }
    ]
   },
   {
    "franchise": [
     {
      "id": "0004",
      "score": ""
     },
     {
      "id": "0011",
      "score": ""
     }
    ]
   },
   {
    "franchise": [
     {
      "id": "0005",
      "score": ""
     },
     {
      "id": "0010",
      "score": ""
     }
    ]
   },
   {
    "franchise": [
     {
      "id": "0006",
      "score": ""
     },
     {
      "id": "0009",
      "score": ""
     }
    ]
   },
   {
    "franchise": [
     {
      "id": "0007",
      "score": ""
     },
     {
      "id": "0008",
      "score": ""
     }
    ]
   }
  ]
 }
}
