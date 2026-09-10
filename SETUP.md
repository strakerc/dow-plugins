# Setting up the Dynasty of Whiners league tools

This adds a set of league skills to your own Claude account: rules and cap
questions, contract decisions, who owns which pick, franchise tag prices, trade
evaluation, weekly lineups, and the member directory. Everything it tells you
comes live from MyFantasyLeague — it holds no saved copy of the league.

Ten minutes, two pastes, and one thing to get right before you start.

---

## Before you start: it has to be a personal Claude account

**Team and Enterprise accounts cannot add their own connectors.** The option
does not appear at all — nothing is broken, it simply is not there. If your
Claude account is through work, use a personal one for this.

A paid plan is not required for the setup itself.

---

## Step 1 — Add the marketplace

In Claude, go to **Customize** in the left sidebar, then the **Plugins** tab.

Use **Add** at the top right and give it this address:

```
https://github.com/strakerc/dow-plugins
```

Two plugins will appear:

| Plugin | Who installs it |
|---|---|
| **Dow league** | **Everyone.** All the owner tools. |
| **Dow league lm** | Only if Straker has told you that you are an LM. |

Install **Dow league**. Skip the LM one unless it applies to you — its skills
need permissions your key does not carry, so installing it just adds clutter.

### Turn on automatic sync

In the same Plugins tab, open **Manage marketplaces**, then the **⋮** menu next
to `dow-plugins`, and switch on **Sync automatically**.

**You have to reach this from Customize in the left sidebar** — not from your
account menu at the bottom left. Both routes look like the same page. Only the
sidebar one shows the sync option, and on the other it is simply absent rather
than greyed out, so there is nothing to tell you that you are in the wrong place.

Skills get corrected fairly often. With sync off you keep whatever version you
installed on the day you installed it, including its mistakes, and nothing tells
you that you are behind.

---

## Step 2 — Add your connector

**Ask Straker for your personal Dynasty of Whiners connector URL.** Every owner
gets their own. Do not share it and do not use someone else's — it identifies
you to the league tools, and the answers you get are shaped by which team is
yours.

Then add it at **claude.ai → Customize → Connectors**. It is one paste.

That is the whole setup.

---

## Step 3 — Check it works

Start a **new** chat and ask something only the league tools can answer:

> What is my roster?

A good answer names your actual players. If instead you get a general reply
about fantasy football, or Claude says it cannot see any league tools, go to
[When it does not work](#when-it-does-not-work).

---

## Things worth knowing

**An update needs a new chat.** Skills are loaded when a task starts, so a
plugin that updates mid-conversation does not appear until you begin a new one.
Start a new chat rather than uninstalling and reinstalling.

**It is inert without your connector.** The plugin ships no key and no league
data. That is deliberate: it is the reason a public repository is safe to
install from.

**It reads; it does not write.** Nothing here changes your roster, submits a
lineup, accepts a trade, or posts to Discord on your behalf. Entering a lineup
is still something you do yourself in MFL.

**Ask in plain language.** "Should I start Bijan or Judkins this week", "what
happens to the cap if I cut him", "who owns my 2028 second". You do not need to
name a skill or a tool.

**It can be wrong.** Everything comes from live MFL data, but the reasoning on
top of it is Claude's. Check anything you are about to act on, and tell Straker
when something looks off — several of these skills exist in their current shape
because someone did exactly that.

---

## When it does not work

**Claude does not seem to know about the league at all**
The connector is not set up, or you asked in a chat that started before you
added it. Start a new chat first. If it still happens, re-check Step 2.

**"Unknown tool"**
This is a key problem, not a broken skill — a tool your key cannot reach reports
as unknown rather than as a permission error. Ask Straker.

**A 401, or a message about the key**
Your key is wrong or has been revoked. Ask Straker for a new connector URL. A
newly issued URL replaces your old one, so remove the old connector when you add
the replacement.

**"Connectors" does not appear in Customize**
Team or Enterprise account. See the top of this page.

**Something is out of date**
Open **Manage marketplaces**, the **⋮** menu, then **Check for updates**. If you
turned on automatic sync in Step 1 you should not need this.

---

## Questions

Ask Straker. If something in this page is wrong or unclear, say so — it is
easier to fix here once than to answer eleven times.
