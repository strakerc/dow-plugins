---
type: llm
criteria: "Says plainly that the trade evaluator prices proposals, not completed trades, even though the owner asked for it by name. Then either (a) runs it anyway, is refused (Kai Mercer is on Bram's roster, not Ada's), calls the refusal the tool working because the trade already went through, and offers or does a reversed run saying it inverted the sides or points to trade history; or (b) hands off to trade history before calling it and reports the recorded trade (Ada sent Kai Mercer and her 2028 1st to Bram for Ravi Dunn and a 2026 rookie pick, 31 Jul 2026 PT). Never drops an asset and retries, never calls the tool broken, and never invents a verdict from the evaluator."
---
The section under test says a completed trade is not the evaluator's to
score and that trade history is the skill for it. Recognising that before
the call is that section working at least as well as recognising it after
the refusal, so route (b) passes. The mock refuses every call with the same
message, so an answer that tried a reversed run, got the same refusal, and
then handed off to trade history still passes. A market-value read offered
as a substitute is fine only if the answer also says the evaluator does not
price completed trades. Fail an answer that scores the trade as a proposal,
drops Kai Mercer and scores the rest, or calls the tool glitchy or broken.
