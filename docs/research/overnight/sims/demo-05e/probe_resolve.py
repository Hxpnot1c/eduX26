"""Which words in the Plan A lines pull a course part into focus (example-mini pack)? A literacy turn whose message
resolves to a course part makes that part the focus, and the focus then sticks for later turns.
    EDUX_DATA_DIR=<loaded data dir> PYTHONPATH=<code copy> python probe_resolve.py"""
import re
from edux import graph

LINES = [
    "what's happening with inflation?",
    "What happened to UK CPI inflation in 2025, and why? Please give me sources I can check.",
    "That ONS link doesn't work.",
    "That link doesn't work.",
    "That ONS link is broken.",
    "The ONS link is dead.",
    "That ONS link goes nowhere.",
    "That link is dead.",
    "The link's dead.",
    "What was UK CPI inflation in 2025, and why? Give me sources I can check.",
    "What was UK CPI inflation in 2025 and why did it change? Sources please.",
    "Why did UK CPI inflation change in 2025? Give sources.",
    "What was UK inflation in 2025?",
    "how much does petrol cost?",
    "What was UK CPI inflation in 2025, and why did it change? Sources please.",
    "What was UK CPI inflation in 2025, and why? Sources please.",
    "What was UK CPI inflation in 2025 and why? Please show sources.",
    "That page doesn't exist.",
    "That web address doesn't open.",
    "That address doesn't open.",
    "I tried that ONS page and it doesn't exist.",
    "I clicked it and the page doesn't exist.",
    "I clicked the first source and the page doesn't exist.",
    "The first source doesn't open.",
    "I checked: that page doesn't exist.",
    "That ONS page doesn't give that figure.",
    "That page doesn't say that.",
    "I checked that page and it shows a different figure.",
    "I checked: the page says something different.",
    "I opened it and the number on the page is different.",
    "tell me about inflation",
    "is inflation bad?",
    "why does inflation matter?",
    "what does inflation do?",
    "what was inflation like?",
    "I opened it and the page says 9.1%, not 11.1%.",
    "I opened it, but the page says 9.1% for that month, not 11.1%.",
    "I opened it and that page says 9.1%, not 11.1%.",
    "what was inflation?",
]
for line in LINES:
    r = graph.resolve(line, [])
    words = [w for w in re.findall(r"[A-Za-z0-9']+", line)]
    hits = {w: graph.resolve(w, [])["parts"] for w in words}
    hits = {w: p for w, p in hits.items() if p}
    print(f"{line!r}\n   -> parts {r['parts']} candidates {[c['id'] for c in r['candidates']]}; words that match: {hits}")
