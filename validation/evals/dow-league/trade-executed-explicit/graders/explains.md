---
type: llm
criteria: "Says plainly that the trade evaluator prices proposals, not completed trades, even though the owner asked for it by name. Then either (a) runs it, is refused because the 2026 rookie pick 2.04 is from a draft already held, calls the refusal the tool working since the trade already went through, and offers or does a reversed run saying it inverted the sides or points to trade history; or (b) hands off to trade history before calling it and reports the recorded trade (Ada sent Kai Mercer and her 2028 1st to Bram for Ravi Dunn and the 2026 2.04, 31 Jul 2026 PT). Never drops an asset and retries, never calls the tool broken or buggy, and never invents an evaluator verdict."
---
The section under test says a completed trade is not the evaluator's to
score and that trade history is the skill for it. Recognising that before
the call is that section working at least as well as recognising it after
the refusal, so route (b) passes. The refusal names the settled 2026 pick,
which is untradeable in either direction, so a reversed run refused the
same way is consistent, and an answer that then hands off to trade history
passes. A market-value read offered alongside is fine if the answer also
says the evaluator does not price completed trades. Fail an answer that
scores the trade as a proposal, drops the pick and scores the rest, or
calls the tool glitchy, buggy or broken.
