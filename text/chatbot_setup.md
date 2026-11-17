# Setting up your chatbot

1. Add eduX as a connector (also called a custom connector or MCP server) in your chatbot's settings, using the link your teacher gave you. It looks like https://<server>/mcp?key=<your key>. Your key is personal: don't share it.
2. Paste the text below into your chatbot's custom instructions (sometimes called "personal preferences" or "instructions for this project").

---

I'm studying for my exams. Call tutor_turn at the start of every reply, including questions about the world, and follow the plan it returns. Keep replies short. Don't do my homework for me.

---

3. Check it works: ask "What should I work on next?" The chatbot should call get_my_progress and talk you through it.
