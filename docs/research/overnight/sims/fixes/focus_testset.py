"""w4-fix-focus test set: 64 student messages in our own words (written before any patch; labels frozen).

Each row: (category, request_type a chatbot would send, message, expected).
expected = None: no course part of example-mini should become the focus (the pack covers only elasticities and
indirect taxes / market failure). Otherwise a tuple of node ids: a resolution is right if every resolved part sits
under one of them (or a candidate does). Categories: R research (economics news/data), V verify follow-ups in a
literacy episode, H homework (course questions), N name-word traps (common words that appear in part names),
C chit-chat.
"""
R, V, H, N, C = "research", "verify", "homework", "nameword", "chat"
ELAST, TAX = "elasticities", "indirect_taxes"

TESTSET = [
    # --- research questions about economics news / data ---
    (R, "research", "Why are food prices still going up in the UK? Can you link me to where the numbers come from?", None),
    (R, "research", "What did the Bank of England do with interest rates this year and why?", None),
    (R, "research", "How many people are unemployed in the UK right now? Give me the ONS figure.", None),
    (R, "research", "Is the UK in a recession? Show me the GDP data.", None),
    (R, "research", "What was the inflation rate in October and what caused it?", None),
    (R, "research", "Did the sugar tax actually make fizzy drinks less sugary? Sources please.", ("externality_tax", "tax_incidence")),
    (R, "research", "How much of fuel duty do drivers actually pay compared with the petrol companies?", ("tax_incidence",)),
    (R, "research", "When cigarette taxes went up, did people smoke less? Find me a study.", ("ped", TAX)),
    (R, "research", "How did UK petrol prices change in 2025, and how did demand respond?", ("ped",)),
    (R, "research", "What are economists saying about the minimum wage rise next April?", None),
    (R, "research", "Why is the pound weaker against the dollar this month?", None),
    (R, "research", "Has the cost of living crisis ended? What does the latest data say?", None),
    (R, "research", "What's the latest house price index for London?", None),
    (R, "research", "How much does the government borrow each year? Link to the OBR please.", None),
    (R, "research", "Which countries have the highest inflation at the moment?", None),
    (R, "research", "Did the plastic bag charge cut how many bags people use? I want the first study that measured it.", ("externality_tax",)),
    (R, "research", "What does the latest ONS release say about wages growing faster than prices?", None),
    (R, "research", "Are energy bills going up again in January? Different suppliers seem to say different things.", None),
    (R, "research", "Show me a chart of UK interest rates over the last ten years.", None),
    (R, "research", "Who pays the most income tax in the UK, rich or poor households?", None),
    (R, "research", "What happened to train fares this year and why did they rise so much?", None),
    (R, "research", "Is it true that the UK has the lowest productivity in the G7? Give me a source.", None),
    # --- verify follow-ups inside a literacy episode ---
    (V, "other", "That link doesn't work.", None),
    (V, "other", "I clicked the first source and the page doesn't exist.", None),
    (V, "other", "The ONS page shows a different number to the one you gave.", None),
    (V, "other", "That article is from 2019, not this year.", None),
    (V, "other", "Are you sure? The BBC says something else.", None),
    (V, "research", "Where did you get that figure from?", None),
    (V, "other", "Your source is a blog, is that reliable?", None),
    (V, "research", "Can you double check that number for me?", None),
    # --- homework / course questions ---
    (H, "concept", "How do I calculate price elasticity of demand?", ("ped",)),
    (H, "concept", "Why is demand for insulin inelastic?", ("ped",)),
    (H, "concept", "If PED is -0.4 what happens to revenue when the price goes up?", ("ped",)),
    (H, "concept", "What makes the supply of houses so slow to react to price?", ("pes",)),
    (H, "concept", "What's the difference between normal and inferior goods?", ("yed",)),
    (H, "concept", "Who pays more of a tax when demand is inelastic?", ("tax_incidence", "ped")),
    (H, "concept", "How do I draw a diagram for a specific tax on cigarettes?", ("tax_incidence",)),
    (H, "concept", "Evaluate whether a tax on sugary drinks is a good idea.", ("externality_tax", "tax_incidence")),
    (H, "concept", "What's a Pigouvian tax?", ("externality_tax",)),
    (H, "concept", "How do you work out the percentage changes for an elasticity?", (ELAST,)),
    (H, "concept", "Is a YED of 2 a luxury?", ("yed",)),
    (H, "concept", "What's the difference between ad valorem and specific taxes?", ("tax_incidence",)),
    (H, "concept", "My teacher says elastic means bigger than one, why?", ("ped",)),
    (H, "concept", "What are the determinants of price elasticity of supply?", ("pes",)),
    (H, "concept", "Why do firms care about elasticity when they set prices?", (ELAST,)),
    (H, "concept", "How do I answer an 8 marker on market failure?", (TAX,)),
    (H, "concept", "What's the multiplier effect?", None),
    (H, "concept", "How does quantitative easing work?", None),
    (H, "concept", "Can you help with my essay on monopoly?", None),
    (H, "concept", "What's the difference between GDP and GNI?", None),
    # --- traps: everyday or off-pack questions using words that appear in part names ---
    (N, "concept", "Give me a definition of GDP.", None),
    (N, "concept", "What is aggregate demand made up of?", None),
    (N, "concept", "What's the formula for the multiplier?", None),
    (N, "concept", "What does the Phillips curve show about prices and wages?", None),
    # --- chit-chat ---
    (C, "other", "hi", None),
    (C, "other", "thanks, that really helped", None),
    (C, "other", "I'm so tired, I've got three tests this week", None),
    (C, "other", "can we do something different?", None),
    (C, "other", "lol ok", None),
    (C, "other", "I have to give my presentation first thing tomorrow, wish me luck", None),
    (C, "other", "Does this cost money to use?", None),
    (C, "other", "show me what you can do", None),
    (C, "other", "my link to the school portal isn't working", None),
    (C, "other", "can you give me a quick quiz on anything?", None),
]
