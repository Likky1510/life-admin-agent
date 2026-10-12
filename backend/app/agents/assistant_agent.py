"""
AI Assistant (Module 5).

The chatbot pulls in three kinds of context before responding:
  1. Recent conversation history (normal chat continuity)
  2. The user's current life items (so it can actually help plan, not
     just chat generically)
  3. Relevant long-term memories from ChromaDB (so repeated preferences
     surface even across sessions, not just within one conversation)
"""
from datetime import datetime
from app.agents.claude_client import call_claude_text, call_claude_json
from app.memory.chroma_memory import recall_memories, add_memory

CHAT_SYSTEM_PROMPT = """You are a helpful, encouraging personal life-admin assistant.
You help the user manage tasks, bills, appointments, and deadlines, and you help them
discover and plan around career/educational opportunities. Be concise and practical.
If the user's question relates to something in their current tasks or past preferences
(provided as context), reference it naturally. Don't be repetitive or robotic."""


def _format_life_items_context(items: list) -> str:
    if not items:
        return "The user currently has no tracked tasks, bills, or appointments."
    lines = [f"- [{i.item_type.value}] {i.title} due {i.due_date.strftime('%Y-%m-%d %H:%M')}" for i in items]
    return "Current life items:\n" + "\n".join(lines)


def chat_with_assistant(user_message: str, user_id: str, life_items: list, conversation_history: list) -> str:
    """
    conversation_history: list of {"role": "user"|"assistant", "content": str},
    most-recent-last, already trimmed by the caller to a reasonable length.
    """
    memories = recall_memories(user_id, user_message, n_results=3)
    memory_context = ("Relevant things you've noted about this user before:\n" + "\n".join(f"- {m}" for m in memories)) if memories else ""

    items_context = _format_life_items_context(life_items)

    full_context = f"{items_context}\n\n{memory_context}".strip()
    user_prompt = f"Context:\n{full_context}\n\nUser message: {user_message}"

    mock_reply = (
        f"[mock reply] I see you have {len(life_items)} tracked item(s). "
        "Once a real Claude API key is configured, I'll give you a tailored response here."
    )

    reply = call_claude_text(
        system_prompt=CHAT_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        mock_response=mock_reply,
        conversation_history=conversation_history,
    )

    # Store this exchange as a memory if it reveals a preference worth
    # remembering long-term (heuristic: longer, more specific messages are
    # more likely to contain a real preference than a one-word reply)
    if len(user_message.split()) >= 6:
        add_memory(user_id, f"User said: {user_message}", metadata={"type": "chat", "timestamp": datetime.utcnow().isoformat()})

    return reply


SCHEDULE_SYSTEM_PROMPT = """You are a productivity assistant. Given a list of a user's
tasks/bills/appointments due soon, suggest a sensible order to tackle them today and a
short encouraging summary.

Respond with ONLY a JSON object, no preamble, no markdown fences:
{
  "schedule": [<ordered list of 3-6 short action items for today>],
  "summary": "<one encouraging sentence summarizing the day ahead>"
}
"""


def suggest_daily_schedule(life_items: list) -> dict:
    if not life_items:
        return {"schedule": [], "summary": "Nothing urgent today -- a good day to get ahead on something."}

    items_text = "\n".join(
        f"- [{i.item_type.value}] {i.title}, due {i.due_date.strftime('%Y-%m-%d %H:%M')}"
        for i in sorted(life_items, key=lambda x: x.due_date)
    )

    mock_schedule = [f"Handle: {i.title}" for i in sorted(life_items, key=lambda x: x.due_date)[:5]]
    mock = {
        "schedule": mock_schedule,
        "summary": f"You have {len(life_items)} item(s) coming up -- tackle the earliest deadlines first.",
    }

    result = call_claude_json(
        system_prompt=SCHEDULE_SYSTEM_PROMPT,
        user_prompt=f"Items due soon:\n{items_text}",
        mock_response=mock,
    )
    result["schedule"] = result.get("schedule", []) or []
    result["summary"] = result.get("summary", "")
    return result


SUMMARY_SYSTEM_PROMPT = """You are an assistant summarizing career/educational opportunities
for a student. Given a list of opportunities, write a short 2-3 sentence summary
highlighting the most relevant or time-sensitive ones."""


def summarize_opportunities(opportunities: list) -> str:
    if not opportunities:
        return "No opportunities found matching your profile right now -- check back soon."

    mock = (
        f"You have {len(opportunities)} matching opportunities right now. "
        f"The top match is '{opportunities[0]['title']}' at {opportunities[0].get('organization', 'an organization')} -- worth a look."
    )

    opp_text = "\n".join(f"- {o['title']} at {o.get('organization', '')}: {o.get('description', '')}" for o in opportunities[:10])
    return call_claude_text(
        system_prompt=SUMMARY_SYSTEM_PROMPT,
        user_prompt=f"Opportunities:\n{opp_text}",
        mock_response=mock,
    )
