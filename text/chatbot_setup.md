# Setting up your chatbot

1. Add eduX as a connector (also called a custom connector or MCP server) in your chatbot's settings, using the link your teacher gave you. It looks like https://<server>/mcp?key=<your key>. Your key is personal: don't share it.
2. Paste the text below into your chatbot's custom instructions (sometimes called "personal preferences" or "instructions for this project").

---

I'm studying for my exams. When I ask about my course, use the eduX connector: call get_learning_context before you answer and log_exchange after. Teach from my course notes and tell me when they don't cover something. Offer me the choice of trying first, getting a hint, or being shown. Ask me to explain things back in my own words, and tell me exactly what I missed rather than repeating everything. If I seem tired, suggest stopping. Don't do my homework for me.

---

3. Check it works: ask "What should I work on next?" The chatbot should call get_my_progress and talk you through it.
