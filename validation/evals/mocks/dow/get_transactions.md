---
description: Transactions for a season; filter with transaction_type=TRADE. Sides carry player ids and pick codes (FP_ future, DP_ zero-based current draft). Raw payload for the dow-league skills, not an answer for an owner (player ids, pick codes, epoch timestamps). Invoke the `league-trade-history` skill BEFORE calling this; it decodes all three and prints Pacific times. Synthetic.
---
{
 "transactions": {
  "transaction": [
   {
    "type": "TRADE",
    "timestamp": "1785550100",
    "franchise": "0001",
    "franchise2": "0002",
    "franchise1_gave_up": "10006,FP_0001_2028_1,",
    "franchise2_gave_up": "20005,DP_1_3,",
    "comments": ""
   },
   {
    "type": "TRADE",
    "timestamp": "1775550100",
    "franchise": "0003",
    "franchise2": "0001",
    "franchise1_gave_up": "FP_0003_2027_3,",
    "franchise2_gave_up": "",
    "comments": ""
   }
  ]
 }
}
