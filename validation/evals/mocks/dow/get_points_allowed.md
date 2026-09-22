---
description: "Fantasy points each NFL defence has allowed per position (QB, RB, WR, TE) under THIS league's scoring. Per team: `games`, and for each position the season total `points`, `per_game` and `rank` -- rank 1 allows the FEWEST per game, so a HIGH rank is a soft matchup for that position. Covers completed weeks only, named in `through_week`; the week in progress is not in it, and early in a season a rank rests on one or two games, so say how many. Team `id` is the MFL code, the same as `team` on a roster row and `id` in get_nfl_schedule, which is where a player's opponent that week comes from. Context beside a projection, never added to it: the projection already prices the matchup. Raw payload for the dow-league skills, not an answer for an owner. Invoke the `league-lineup` skill BEFORE calling this. Synthetic: the twelve NFL teams the synthetic league rosters, two games each."
---
{
 "version": "1.0",
 "encoding": "utf-8",
 "pointsAllowed": {
  "season": "2026",
  "through_week": 2,
  "ranked_teams": 12,
  "note": "Fantasy points allowed per position under this league's scoring. `points` is MFL's running season total; `per_game` divides it by `games`, the team's games in weeks 1 to `through_week`; `rank` 1 allows the fewest per game and the highest rank allows the most. MFL's totals lag, so the week in progress is not in them. A rank resting on one or two games is a small sample: say how many.",
  "team": [
   {
    "id": "DAL",
    "games": 2,
    "QB": {
     "points": 40.0,
     "per_game": 20.0,
     "rank": 7
    },
    "RB": {
     "points": 46.8,
     "per_game": 23.4,
     "rank": 7
    },
    "WR": {
     "points": 69.02,
     "per_game": 34.51,
     "rank": 9
    },
    "TE": {
     "points": 33.4,
     "per_game": 16.7,
     "rank": 12
    }
   },
   {
    "id": "GB",
    "games": 2,
    "QB": {
     "points": 34.4,
     "per_game": 17.2,
     "rank": 5
    },
    "RB": {
     "points": 56.4,
     "per_game": 28.2,
     "rank": 10
    },
    "WR": {
     "points": 60.36,
     "per_game": 30.18,
     "rank": 7
    },
    "TE": {
     "points": 15.8,
     "per_game": 7.9,
     "rank": 4
    }
   },
   {
    "id": "SEA",
    "games": 2,
    "QB": {
     "points": 42.8,
     "per_game": 21.4,
     "rank": 8
    },
    "RB": {
     "points": 37.2,
     "per_game": 18.6,
     "rank": 4
    },
    "WR": {
     "points": 56.04,
     "per_game": 28.02,
     "rank": 6
    },
    "TE": {
     "points": 9.2,
     "per_game": 4.6,
     "rank": 1
    }
   },
   {
    "id": "PIT",
    "games": 2,
    "QB": {
     "points": 54.0,
     "per_game": 27.0,
     "rank": 12
    },
    "RB": {
     "points": 53.2,
     "per_game": 26.6,
     "rank": 9
    },
    "WR": {
     "points": 77.68,
     "per_game": 38.84,
     "rank": 11
    },
    "TE": {
     "points": 31.2,
     "per_game": 15.6,
     "rank": 11
    }
   },
   {
    "id": "BUF",
    "games": 2,
    "QB": {
     "points": 48.4,
     "per_game": 24.2,
     "rank": 10
    },
    "RB": {
     "points": 27.6,
     "per_game": 13.8,
     "rank": 1
    },
    "WR": {
     "points": 73.34,
     "per_game": 36.67,
     "rank": 10
    },
    "TE": {
     "points": 13.6,
     "per_game": 6.8,
     "rank": 3
    }
   },
   {
    "id": "DET",
    "games": 2,
    "QB": {
     "points": 51.2,
     "per_game": 25.6,
     "rank": 11
    },
    "RB": {
     "points": 30.8,
     "per_game": 15.4,
     "rank": 2
    },
    "WR": {
     "points": 43.06,
     "per_game": 21.53,
     "rank": 3
    },
    "TE": {
     "points": 20.2,
     "per_game": 10.1,
     "rank": 6
    }
   },
   {
    "id": "MIA",
    "games": 2,
    "QB": {
     "points": 28.8,
     "per_game": 14.4,
     "rank": 3
    },
    "RB": {
     "points": 43.6,
     "per_game": 21.8,
     "rank": 6
    },
    "WR": {
     "points": 51.7,
     "per_game": 25.85,
     "rank": 5
    },
    "TE": {
     "points": 24.6,
     "per_game": 12.3,
     "rank": 8
    }
   },
   {
    "id": "LAR",
    "games": 2,
    "QB": {
     "points": 37.2,
     "per_game": 18.6,
     "rank": 6
    },
    "RB": {
     "points": 34.0,
     "per_game": 17.0,
     "rank": 3
    },
    "WR": {
     "points": 47.38,
     "per_game": 23.69,
     "rank": 4
    },
    "TE": {
     "points": 22.4,
     "per_game": 11.2,
     "rank": 7
    }
   },
   {
    "id": "DEN",
    "games": 2,
    "QB": {
     "points": 23.2,
     "per_game": 11.6,
     "rank": 1
    },
    "RB": {
     "points": 62.8,
     "per_game": 31.4,
     "rank": 12
    },
    "WR": {
     "points": 82.0,
     "per_game": 41.0,
     "rank": 12
    },
    "TE": {
     "points": 26.8,
     "per_game": 13.4,
     "rank": 9
    }
   },
   {
    "id": "KC",
    "games": 2,
    "QB": {
     "points": 26.0,
     "per_game": 13.0,
     "rank": 2
    },
    "RB": {
     "points": 50.0,
     "per_game": 25.0,
     "rank": 8
    },
    "WR": {
     "points": 34.4,
     "per_game": 17.2,
     "rank": 1
    },
    "TE": {
     "points": 11.4,
     "per_game": 5.7,
     "rank": 2
    }
   },
   {
    "id": "PHI",
    "games": 2,
    "QB": {
     "points": 45.6,
     "per_game": 22.8,
     "rank": 9
    },
    "RB": {
     "points": 40.4,
     "per_game": 20.2,
     "rank": 5
    },
    "WR": {
     "points": 38.72,
     "per_game": 19.36,
     "rank": 2
    },
    "TE": {
     "points": 18.0,
     "per_game": 9.0,
     "rank": 5
    }
   },
   {
    "id": "SF",
    "games": 2,
    "QB": {
     "points": 31.6,
     "per_game": 15.8,
     "rank": 4
    },
    "RB": {
     "points": 59.6,
     "per_game": 29.8,
     "rank": 11
    },
    "WR": {
     "points": 64.7,
     "per_game": 32.35,
     "rank": 8
    },
    "TE": {
     "points": 29.0,
     "per_game": 14.5,
     "rank": 10
    }
   }
  ]
 }
}
