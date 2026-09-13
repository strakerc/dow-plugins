---
description: Every franchise's roster with salary, contract type, contract end year and taxi/IR status, and on every player row his name, position and NFL team. `contractStatus` is the FINAL year of the deal, so years remaining = contractStatus - season + 1. A row with no name is a player MFL no longer lists; get_players is only for extended details. Pass season for that season's end-of-season snapshot (the payload echoes it), franchise_id for one team. Raw payload for the dow-league skills, not an answer for an owner (player ids, contract fields). Invoke the `league-contracts` skill for contract questions, `league-franchise-tags` for tag floors, or `league-player-status` for who has a player BEFORE calling this. Synthetic.
---
{
 "rosters": {
  "season": "{{input.season}}",
  "franchise": [
   {
    "id": "0001",
    "player": [
     {
      "id": "10001",
      "name": "Vance, Tobias",
      "position": "QB",
      "team": "SEA",
      "salary": "40.00",
      "contractInfo": "Long-Term",
      "contractYear": "2",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "10002",
      "name": "Hale, Marcus",
      "position": "RB",
      "team": "PIT",
      "salary": "22.00",
      "contractInfo": "Short-Term",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     },
     {
      "id": "10003",
      "name": "Brandt, Elliot",
      "position": "WR",
      "team": "DEN",
      "salary": "18.00",
      "contractInfo": "Long-Term",
      "contractYear": "3",
      "contractStatus": "2026",
      "status": "ROSTER"
     },
     {
      "id": "10004",
      "name": "Pike, Rowan",
      "position": "TE",
      "team": "KC",
      "salary": "6.00",
      "contractInfo": "Rookie",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "TAXI_SQUAD",
      "drafted": "2.02 (2026)"
     },
     {
      "id": "10005",
      "name": "Orr, Silas",
      "position": "RB",
      "team": "BUF",
      "salary": "30.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "INJURED_RESERVE"
     },
     {
      "id": "10007",
      "name": "Reyes, Jonah",
      "position": "QB",
      "team": "PHI",
      "salary": "15.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "10008",
      "name": "Bell, Cyrus",
      "position": "RB",
      "team": "SF",
      "salary": "10.00",
      "contractInfo": "Rookie",
      "contractYear": "2",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "1.08 (2025)"
     },
     {
      "id": "10009",
      "name": "Marsh, Felix",
      "position": "WR",
      "team": "MIA",
      "salary": "14.00",
      "contractInfo": "Long-Term",
      "contractYear": "2",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "10010",
      "name": "Castillo, Wren",
      "position": "WR",
      "team": "LAR",
      "salary": "3.00",
      "contractInfo": "Rookie",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER",
      "drafted": "3.04 (2026)"
     },
     {
      "id": "10011",
      "name": "Lindqvist, Bo",
      "position": "TE",
      "team": "DAL",
      "salary": "20.00",
      "contractInfo": "Long-Term",
      "contractYear": "2",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "10012",
      "name": "Okafor, Ansel",
      "position": "RB",
      "team": "GB",
      "salary": "5.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $5"
     },
     {
      "id": "10013",
      "name": "Sol, Dmitri",
      "position": "QB",
      "team": "SEA",
      "salary": "3.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $3"
     },
     {
      "id": "10014",
      "name": "Ferro, Luca",
      "position": "WR",
      "team": "PIT",
      "salary": "4.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $4"
     },
     {
      "id": "10015",
      "name": "Voss, Harlan",
      "position": "RB",
      "team": "DEN",
      "salary": "2.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $2"
     },
     {
      "id": "20005",
      "name": "Dunn, Ravi",
      "position": "TE",
      "team": "SF",
      "salary": "7.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $7"
     },
     {
      "id": "40013",
      "name": "Abernook, Arno",
      "position": "WR",
      "team": "DAL",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40014",
      "name": "Abernook, Holt",
      "position": "RB",
      "team": "GB",
      "salary": "40.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40015",
      "name": "Abernook, Orrin",
      "position": "WR",
      "team": "SEA",
      "salary": "3.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0002",
    "player": [
     {
      "id": "20001",
      "name": "Lane, Victor",
      "position": "QB",
      "team": "KC",
      "salary": "35.00",
      "contractInfo": "Long-Term",
      "contractYear": "2",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "20002",
      "name": "Sato, Nico",
      "position": "RB",
      "team": "BUF",
      "salary": "25.00",
      "contractInfo": "Short-Term",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     },
     {
      "id": "20003",
      "name": "Frost, Owen",
      "position": "WR",
      "team": "DET",
      "salary": "30.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "20004",
      "name": "Alvarez, Teo",
      "position": "WR",
      "team": "PHI",
      "salary": "8.00",
      "contractInfo": "Rookie",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER",
      "drafted": "1.11 (2026)"
     },
     {
      "id": "20006",
      "name": "Grant, Milo",
      "position": "RB",
      "team": "MIA",
      "salary": "12.00",
      "contractInfo": "Long-Term",
      "contractYear": "2",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "20007",
      "name": "Quist, Sam",
      "position": "QB",
      "team": "LAR",
      "salary": "9.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $9"
     },
     {
      "id": "20008",
      "name": "Park, Jude",
      "position": "WR",
      "team": "DAL",
      "salary": "6.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $6"
     },
     {
      "id": "20009",
      "name": "Reilly, Ash",
      "position": "WR",
      "team": "GB",
      "salary": "5.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $5"
     },
     {
      "id": "20010",
      "name": "Diaz, Oren",
      "position": "RB",
      "team": "SEA",
      "salary": "4.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $4"
     },
     {
      "id": "20011",
      "name": "Kade, Ira",
      "position": "TE",
      "team": "PIT",
      "salary": "3.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $3"
     },
     {
      "id": "10006",
      "name": "Mercer, Kai",
      "position": "WR",
      "team": "DET",
      "salary": "12.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER",
      "drafted": "Auction $12"
     },
     {
      "id": "40016",
      "name": "Brackwell, Bex",
      "position": "QB",
      "team": "PIT",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40017",
      "name": "Brackwell, Idris",
      "position": "TE",
      "team": "BUF",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40018",
      "name": "Brackwell, Peir",
      "position": "RB",
      "team": "DET",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40019",
      "name": "Coldry, Corin",
      "position": "WR",
      "team": "MIA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40020",
      "name": "Coldry, Jory",
      "position": "TE",
      "team": "LAR",
      "salary": "10.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40021",
      "name": "Coldry, Quill",
      "position": "RB",
      "team": "DEN",
      "salary": "1.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0003",
    "player": [
     {
      "id": "30001",
      "name": "Ash, Pax",
      "position": "QB",
      "team": "DEN",
      "salary": "10.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30002",
      "name": "Birch, Rue",
      "position": "RB",
      "team": "KC",
      "salary": "11.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30003",
      "name": "Cedar, Tam",
      "position": "WR",
      "team": "BUF",
      "salary": "12.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40022",
      "name": "Dunmore, Dace",
      "position": "WR",
      "team": "KC",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40023",
      "name": "Dunmore, Kael",
      "position": "WR",
      "team": "PHI",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40024",
      "name": "Dunmore, Rook",
      "position": "RB",
      "team": "SF",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40025",
      "name": "Eastrop, Emrys",
      "position": "WR",
      "team": "DAL",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40026",
      "name": "Eastrop, Lusk",
      "position": "QB",
      "team": "GB",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40027",
      "name": "Eastrop, Sten",
      "position": "TE",
      "team": "SEA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40028",
      "name": "Fallow, Faro",
      "position": "RB",
      "team": "PIT",
      "salary": "18.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40029",
      "name": "Fallow, Mael",
      "position": "WR",
      "team": "BUF",
      "salary": "2.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0004",
    "player": [
     {
      "id": "30004",
      "name": "Dune, Uli",
      "position": "QB",
      "team": "PHI",
      "salary": "13.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30005",
      "name": "Elm, Vin",
      "position": "RB",
      "team": "SF",
      "salary": "14.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30006",
      "name": "Fen, Wes",
      "position": "WR",
      "team": "MIA",
      "salary": "15.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40030",
      "name": "Fallow, Tavi",
      "position": "TE",
      "team": "DET",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40031",
      "name": "Glenhart, Gideon",
      "position": "RB",
      "team": "MIA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40032",
      "name": "Glenhart, Nils",
      "position": "WR",
      "team": "LAR",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40033",
      "name": "Harrowby, Arno",
      "position": "WR",
      "team": "DEN",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40034",
      "name": "Harrowby, Holt",
      "position": "RB",
      "team": "KC",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40035",
      "name": "Harrowby, Orrin",
      "position": "WR",
      "team": "PHI",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40036",
      "name": "Inchcombe, Bex",
      "position": "QB",
      "team": "SF",
      "salary": "34.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40037",
      "name": "Inchcombe, Idris",
      "position": "TE",
      "team": "DAL",
      "salary": "2.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0005",
    "player": [
     {
      "id": "30007",
      "name": "Gale, Xan",
      "position": "QB",
      "team": "DAL",
      "salary": "16.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30008",
      "name": "Heath, Yul",
      "position": "RB",
      "team": "GB",
      "salary": "10.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30009",
      "name": "Isle, Zed",
      "position": "WR",
      "team": "SEA",
      "salary": "11.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40038",
      "name": "Inchcombe, Peir",
      "position": "RB",
      "team": "GB",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40039",
      "name": "Jessop, Corin",
      "position": "WR",
      "team": "SEA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40040",
      "name": "Jessop, Jory",
      "position": "TE",
      "team": "PIT",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40041",
      "name": "Jessop, Quill",
      "position": "RB",
      "team": "BUF",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40042",
      "name": "Kettleby, Dace",
      "position": "WR",
      "team": "DET",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40043",
      "name": "Kettleby, Kael",
      "position": "WR",
      "team": "MIA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40044",
      "name": "Kettleby, Rook",
      "position": "RB",
      "team": "LAR",
      "salary": "3.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     },
     {
      "id": "40045",
      "name": "Longmire, Emrys",
      "position": "WR",
      "team": "DEN",
      "salary": "1.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0006",
    "player": [
     {
      "id": "30010",
      "name": "Jet, Ari",
      "position": "QB",
      "team": "DEN",
      "salary": "12.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30011",
      "name": "Kestrel, Bea",
      "position": "RB",
      "team": "KC",
      "salary": "13.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30012",
      "name": "Lark, Cal",
      "position": "WR",
      "team": "BUF",
      "salary": "14.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40046",
      "name": "Longmire, Lusk",
      "position": "QB",
      "team": "KC",
      "salary": "24.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "INJURED_RESERVE"
     },
     {
      "id": "40047",
      "name": "Longmire, Sten",
      "position": "TE",
      "team": "PHI",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40048",
      "name": "Marrable, Faro",
      "position": "RB",
      "team": "SF",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40049",
      "name": "Marrable, Mael",
      "position": "WR",
      "team": "DAL",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40050",
      "name": "Marrable, Tavi",
      "position": "TE",
      "team": "GB",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40051",
      "name": "Nethercott, Gideon",
      "position": "RB",
      "team": "SEA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40052",
      "name": "Nethercott, Nils",
      "position": "WR",
      "team": "PIT",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40053",
      "name": "Oxenby, Arno",
      "position": "WR",
      "team": "BUF",
      "salary": "7.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0007",
    "player": [
     {
      "id": "30013",
      "name": "Moor, Dov",
      "position": "QB",
      "team": "PHI",
      "salary": "15.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30014",
      "name": "Nettle, Eli",
      "position": "RB",
      "team": "SF",
      "salary": "16.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30015",
      "name": "Oak, Fay",
      "position": "WR",
      "team": "MIA",
      "salary": "10.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40054",
      "name": "Oxenby, Holt",
      "position": "RB",
      "team": "DET",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40055",
      "name": "Oxenby, Orrin",
      "position": "WR",
      "team": "MIA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40056",
      "name": "Pellow, Bex",
      "position": "QB",
      "team": "LAR",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40057",
      "name": "Pellow, Idris",
      "position": "TE",
      "team": "DEN",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40058",
      "name": "Pellow, Peir",
      "position": "RB",
      "team": "KC",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40059",
      "name": "Quarles, Corin",
      "position": "WR",
      "team": "PHI",
      "salary": "7.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0008",
    "player": [
     {
      "id": "30016",
      "name": "Pine, Gil",
      "position": "QB",
      "team": "DAL",
      "salary": "11.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30017",
      "name": "Quarry, Hal",
      "position": "RB",
      "team": "GB",
      "salary": "12.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30018",
      "name": "Reed, Ike",
      "position": "WR",
      "team": "SEA",
      "salary": "13.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40060",
      "name": "Quarles, Jory",
      "position": "TE",
      "team": "SF",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40061",
      "name": "Quarles, Quill",
      "position": "RB",
      "team": "DAL",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40062",
      "name": "Rudstone, Dace",
      "position": "WR",
      "team": "GB",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40063",
      "name": "Rudstone, Kael",
      "position": "WR",
      "team": "SEA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40064",
      "name": "Rudstone, Rook",
      "position": "RB",
      "team": "PIT",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40065",
      "name": "Scarth, Emrys",
      "position": "WR",
      "team": "BUF",
      "salary": "18.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40066",
      "name": "Scarth, Lusk",
      "position": "QB",
      "team": "DET",
      "salary": "2.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0009",
    "player": [
     {
      "id": "30019",
      "name": "Sedge, Jem",
      "position": "QB",
      "team": "DEN",
      "salary": "14.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30020",
      "name": "Thorn, Kel",
      "position": "RB",
      "team": "KC",
      "salary": "15.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30021",
      "name": "Umber, Lex",
      "position": "WR",
      "team": "BUF",
      "salary": "16.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40067",
      "name": "Scarth, Sten",
      "position": "TE",
      "team": "MIA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40068",
      "name": "Tollemy, Faro",
      "position": "RB",
      "team": "LAR",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40069",
      "name": "Tollemy, Mael",
      "position": "WR",
      "team": "DEN",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40070",
      "name": "Tollemy, Tavi",
      "position": "TE",
      "team": "KC",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40071",
      "name": "Underhay, Gideon",
      "position": "RB",
      "team": "PHI",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40072",
      "name": "Underhay, Nils",
      "position": "WR",
      "team": "SF",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40073",
      "name": "Vessey, Arno",
      "position": "WR",
      "team": "DAL",
      "salary": "14.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0010",
    "player": [
     {
      "id": "30022",
      "name": "Vale, Mo",
      "position": "QB",
      "team": "PHI",
      "salary": "10.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30023",
      "name": "Wold, Ned",
      "position": "RB",
      "team": "SF",
      "salary": "11.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30024",
      "name": "Yarrow, Oz",
      "position": "WR",
      "team": "MIA",
      "salary": "12.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40074",
      "name": "Vessey, Holt",
      "position": "RB",
      "team": "GB",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40075",
      "name": "Vessey, Orrin",
      "position": "WR",
      "team": "SEA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40076",
      "name": "Wragby, Bex",
      "position": "QB",
      "team": "PIT",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40077",
      "name": "Wragby, Idris",
      "position": "TE",
      "team": "BUF",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40078",
      "name": "Wragby, Peir",
      "position": "RB",
      "team": "DET",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40079",
      "name": "Yelland, Corin",
      "position": "WR",
      "team": "MIA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40080",
      "name": "Yelland, Jory",
      "position": "TE",
      "team": "LAR",
      "salary": "40.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40081",
      "name": "Yelland, Quill",
      "position": "RB",
      "team": "DEN",
      "salary": "1.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0011",
    "player": [
     {
      "id": "30025",
      "name": "Zinc, Pim",
      "position": "QB",
      "team": "DAL",
      "salary": "13.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30026",
      "name": "Aspen, Quin",
      "position": "RB",
      "team": "GB",
      "salary": "14.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30027",
      "name": "Brook, Rex",
      "position": "WR",
      "team": "SEA",
      "salary": "15.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40082",
      "name": "Ashgrove, Dace",
      "position": "WR",
      "team": "KC",
      "salary": "4.00",
      "contractInfo": "Rookie",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "TAXI_SQUAD",
      "drafted": "3.04 (2026)"
     },
     {
      "id": "40083",
      "name": "Ashgrove, Kael",
      "position": "WR",
      "team": "PHI",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40084",
      "name": "Ashgrove, Rook",
      "position": "RB",
      "team": "SF",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40085",
      "name": "Blenkin, Emrys",
      "position": "WR",
      "team": "DAL",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40086",
      "name": "Blenkin, Lusk",
      "position": "QB",
      "team": "GB",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40087",
      "name": "Blenkin, Sten",
      "position": "TE",
      "team": "SEA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40088",
      "name": "Cadogan, Faro",
      "position": "RB",
      "team": "PIT",
      "salary": "10.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40089",
      "name": "Cadogan, Mael",
      "position": "WR",
      "team": "BUF",
      "salary": "1.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     }
    ]
   },
   {
    "id": "0012",
    "player": [
     {
      "id": "30028",
      "name": "Cliff, Sky",
      "position": "QB",
      "team": "DEN",
      "salary": "16.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30029",
      "name": "Dell, Tor",
      "position": "RB",
      "team": "KC",
      "salary": "10.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "30030",
      "name": "Ember, Ulf",
      "position": "WR",
      "team": "BUF",
      "salary": "11.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2027",
      "status": "ROSTER"
     },
     {
      "id": "40090",
      "name": "Cadogan, Tavi",
      "position": "TE",
      "team": "DET",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40091",
      "name": "Drewery, Gideon",
      "position": "RB",
      "team": "MIA",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40092",
      "name": "Drewery, Nils",
      "position": "WR",
      "team": "LAR",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40093",
      "name": "Elwick, Arno",
      "position": "WR",
      "team": "DEN",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40094",
      "name": "Elwick, Holt",
      "position": "RB",
      "team": "KC",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40095",
      "name": "Elwick, Orrin",
      "position": "WR",
      "team": "PHI",
      "salary": "48.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40096",
      "name": "Farrant, Bex",
      "position": "QB",
      "team": "SF",
      "salary": "10.00",
      "contractInfo": "Long-Term",
      "contractYear": "1",
      "contractStatus": "2028",
      "status": "ROSTER"
     },
     {
      "id": "40097",
      "name": "Farrant, Idris",
      "position": "TE",
      "team": "DAL",
      "salary": "1.00",
      "contractInfo": "Free Agent",
      "contractYear": "1",
      "contractStatus": "2026",
      "status": "ROSTER"
     }
    ]
   }
  ]
 }
}
