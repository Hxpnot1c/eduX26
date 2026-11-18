"""Held-out messages for w4-fix-focus, written AFTER the fixes were designed (not used to tune them).
Same format as focus_testset.TESTSET."""
R, V, H, N, C = "research", "verify", "homework", "nameword", "chat"
HOLDOUT = [
    (R, "research", "What's happening to rents in Manchester? I need numbers for a school project.", None),
    (R, "research", "Why did the government cut national insurance? Who benefits?", None),
    (R, "research", "Is the trade deficit getting bigger? Point me to the official data.", None),
    (R, "research", "What's the current base rate and when does it next change?", None),
    (R, "research", "Did the soft drinks levy raise as much money as they expected?", ("externality_tax", "tax_incidence")),
    (R, "research", "When VAT on energy was cut, did bills actually fall by the full amount?", ("tax_incidence",)),
    (R, "research", "How many people use food banks now compared with five years ago?", None),
    (R, "research", "What do the latest figures say about UK exports to the EU since Brexit?", None),
    (V, "other", "The second link takes me to a page about something else.", None),
    (V, "other", "I looked it up and the real number is lower than yours.", None),
    (V, "research", "Which one of those sources is the most trustworthy?", None),
    (V, "other", "That quote isn't anywhere on the page you sent.", None),
    (H, "concept", "Why is the PES for oil low in the short run?", ("pes",)),
    (H, "concept", "How do I show a subsidy and a tax on the same diagram?", ("tax_incidence",)),
    (H, "concept", "What happens to total revenue if demand is unit elastic?", ("ped",)),
    (H, "concept", "Can you explain income elasticity with an example?", ("yed",)),
    (H, "concept", "What is the difference between a merit good and a public good?", None),
    (H, "concept", "How does a rise in interest rates affect investment?", None),
    (N, "concept", "What values should I put on my axes for a production possibility frontier?", None),
    (N, "concept", "What's the definition of opportunity cost?", None),
    (C, "other", "brb getting food", None),
    (C, "other", "this is actually really useful, I'll tell my friends", None),
    (C, "other", "can you show me the first thing we did today again?", None),
    (C, "other", "sorry I gave the wrong answer before, my cat walked on the keyboard", None),
]
