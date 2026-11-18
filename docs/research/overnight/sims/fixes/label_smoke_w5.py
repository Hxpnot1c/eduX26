"""Smoke test (after a YED turn, so there is a focus to keep): asks_for_reviews through the real MCP server (pydantic ThisMessage), demo-showme, a wording the patterns miss."""
import asyncio, json, sys
sys.path.insert(0, sys.argv[1] + "/scripts")
import check_mcp as C
from edux import learner

async def main(url):
    key = learner.get_student("demo-showme")["key"]
    for label in (True, False):
        with learner._conn() as conn:
            conn.execute("DELETE FROM issued_plan WHERE student_id = 'demo-showme'")
        await C.call(f"{url}?key={key}", "tutor_turn", {"message": "Can you help me with YED?", "node_ids": ["yed_definition"],
              "client": "smoke", "this_message": {"question_depth": "surface", "engagement": "active"}})
        got = await C.call(f"{url}?key={key}", "tutor_turn", {"message": "hit me with a review question", "client": "smoke",
              "this_message": {"question_depth": "surface", "engagement": "active", "asks_for_reviews": label}})
        print(f"asks_for_reviews={label}:", json.dumps([(s["move"], s["part_id"], s["data"].get("purpose")) for s in got.get("plan", [])]) if got.get("ok") else got)
asyncio.run(main(sys.argv[2]))
