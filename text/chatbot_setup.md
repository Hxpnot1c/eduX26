# Setting up your chatbot

1. Add Synapse as a connector (also called a custom connector or MCP server) in your chatbot's settings, using the link your teacher gave you. It looks like https://<server>/mcp?key=<your key>. Your key is personal: don't share it.
2. Paste the text below into your chatbot's custom instructions (sometimes called "personal preferences" or "instructions for this project").

---

I'm studying for my exams. Call tutor_turn at the start of every reply, including questions about the world, and follow the plan it returns. Keep replies short. Don't do my homework for me.

---

3. Check it works: ask "What should I work on next?" The chatbot should call get_my_progress and talk you through it.

## What Synapse keeps, and how to get rid of it

- It keeps what it needs to plan your revision: which topics you have answered questions on and how it went, your reviews, tests you tell it about, your interests line, and how long you took on questions. It does **not** keep your messages to the chatbot or the chatbot's replies.
- It shows you **practice feedback, not a grade**. Your teacher is not sent a score for you from this.
- It does not guess how you feel. If you answer very quickly several times, or you have been going a long time, it may suggest a break or a shorter burst; that is all.
- To see everything it holds about you, or to have it deleted, ask your teacher. If you leave, your data is deleted 90 days later.
- To stop your chatbot company using these chats for training or keeping a memory of them, turn those settings off in the chatbot's own settings (the wording differs between chatbots).
