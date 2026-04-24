import argparse
import yaml
import random
import uuid
import requests
import csv
from openai import OpenAI

# enter keys
OPENAI_API_KEY = ""
GIRL_EFFECT_TOKEN = ""


client = OpenAI(api_key=OPENAI_API_KEY)
API_URL = "https://genai.girleffect.org/intelligence/test/chatbot"


# weighted sampling
def weighted_choice(distribution_dict):
    choices = list(distribution_dict.keys())
    weights = list(distribution_dict.values())
    return random.choices(choices, weights=weights, k=1)[0]


# generate user message (GPT)
def generate_user_message(scenario, history, topic_switch_to=None):
    # [1] freeform prompt: inject extra instruction if provided
    free_form = scenario.get('free_form')
    free_form_line = f"\nAdditional instruction: {free_form}" if free_form else ""

    # [4] clarification tone: if tone is "confused", reinforce in prompt
    tone = scenario.get('tone', '')
    confused_directive = (
        "\nIMPORTANT: Your tone is 'confused' — actively seek clarification. "
        "Say things like 'wait I don't get it', 'can you explain?', ask the chatbot to clarify what they mean."
    ) if tone == "confused" else ""

    # mid-convo topic switch directive
    topic_switch_directive = (
        f"\nIMPORTANT: Abruptly change the subject to '{topic_switch_to}'. "
        "Do NOT continue the previous topic. Start a completely new question about this new topic, "
        "as if you just thought of something else entirely. Make it feel natural but sudden, like a real person texting."
    ) if topic_switch_to else ""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are simulating a REAL young person texting a sexual health chatbot.

Write like a real person:
- casual, imperfect, sometimes unclear
- not overly polished or repetitive

Behavior rules:
- vary how you ask things each time
- sometimes be indirect or hesitant
- sometimes reveal information gradually
- sometimes ask multiple or slightly confusing questions

Do NOT follow the same pattern every conversation.
"""
            },
            {
                "role": "user",
                "content": f"""
Scenario:
- Category: {scenario.get('high_level_category')}
- Topic: {scenario.get('subcategory')}
- Tone: {scenario.get('tone')}
- Barrier: {scenario.get('barrier')}
- Gender: {scenario.get('gender')}
- Age: {scenario.get('age')}
- Edge case: {scenario.get('edge_case')}{free_form_line}

Conversation so far:
{history}
Respond as the USER.{confused_directive}{topic_switch_directive}

Behavior guidance:
- "shy" → indirect, hesitant, not fully explicit
- "knowledge_barrier" → unsure, confused, may not know terms
- "confused" → ask for clarification, say you don't understand, rephrase to seek clarity
Rules:
- 5–25 words
- sound like texting, not formal writing
- do NOT repeat phrasing from earlier turns
- build naturally from the conversation history
Make the message feel human and slightly imperfect.
Output ONLY the user message.
"""
            }
        ]
    )
    return response.choices[0].message.content.strip()


# call chatbot API
def call_chatbot(message, history):
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {GIRL_EFFECT_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "message_text": message,
            "user_id": "poc_user",
            "message_id": str(uuid.uuid4()),
            "conversation_id": "conv-poc",
            "history": history,           # [5] history = previous turns only (not current msg)
            "use_stored_history": False
        },
        timeout=60
    )

    try:
        return response.json()
    except:
        return {"error": response.text, "status": response.status_code}


# run one conversation
def run_conversation(scenario, n_turns, convo_id, switch_topic=None, switch_at_turn=None, subcategory_distribution=None):
    history = []
    rows = []
    current_scenario = dict(scenario)

    # resolve which turn and which topic to switch to
    switch_turn = None
    new_subcategory = None
    if switch_topic and n_turns >= 2:
        # resolve turn (0-indexed internally)
        if switch_at_turn is not None:
            switch_turn = max(1, min(int(switch_at_turn) - 1, n_turns - 1))
        else:
            switch_turn = random.randint(1, n_turns - 1)

        # resolve new topic
        original = current_scenario.get("subcategory")
        if switch_topic == "random":
            candidates = [k for k in (subcategory_distribution or {}) if k != original]
            new_subcategory = random.choice(candidates) if candidates else original
        else:
            new_subcategory = switch_topic

        print(f"[{convo_id}] Topic switch at turn {switch_turn + 1}: '{original}' → '{new_subcategory}'")

    print(f"\n=== Starting Conversation {convo_id} ===")

    for turn in range(n_turns):
        print(f"[{convo_id}] Turn {turn+1}/{n_turns}...")

        # inject topic switch at the designated turn
        topic_switch_directive = None
        if switch_turn is not None and turn == switch_turn:
            topic_switch_directive = new_subcategory
            current_scenario = dict(current_scenario)
            current_scenario["subcategory"] = new_subcategory

        # user — pass history of previous turns only
        user_msg = generate_user_message(current_scenario, history, topic_switch_to=topic_switch_directive)
        print("USER:", user_msg)

        # [5] call bot BEFORE appending current user msg to history
        bot_response = call_chatbot(user_msg, history)
        bot_msg = bot_response.get("message_text", f"ERROR: {bot_response}")

        print("BOT:", bot_msg)

        # append both turns after the bot responds
        history.append({"sender": "user", "text": user_msg})
        history.append({"sender": "bot", "text": bot_msg})

        rows.append({
            "conversation_id": convo_id,
            "turn": turn + 1,
            "user_message": user_msg,
            "bot_response": bot_msg,
            "high_level_category": current_scenario.get("high_level_category"),
            "subcategory": current_scenario.get("subcategory"),
            "tone": current_scenario.get("tone"),
            "barrier": current_scenario.get("barrier"),
            "gender": current_scenario.get("gender"),
            "age": current_scenario.get("age"),
            "edge_case": current_scenario.get("edge_case"),
            "free_form": current_scenario.get("free_form"),
            "topic_switched_at": switch_turn + 1 if switch_turn is not None else None,
            "original_subcategory": scenario.get("subcategory"),
        })

    return rows


# [2] resolve n_turns: int → same for all convos, list → one per convo
def resolve_turns(n_turns_config, n_convos):
    if isinstance(n_turns_config, list):
        if len(n_turns_config) != n_convos:
            raise ValueError(
                f"n_turns list length ({len(n_turns_config)}) must match n_convos ({n_convos})"
            )
        return n_turns_config
    return [int(n_turns_config)] * n_convos


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--selection", type=str, required=True, choices=["manual", "random"])
    parser.add_argument("--n_convos", type=int)
    # [2] n_turns accepts int or comma-separated list, e.g. "3" or "3,4,5"
    parser.add_argument("--n_turns", type=str, help="Integer or comma-separated list matching n_convos")

    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    settings = config.get("settings", {})
    n_convos = args.n_convos or settings.get("n_convos", 1)

    # [2] parse n_turns from CLI or config (int or list)
    if args.n_turns:
        raw = args.n_turns.strip()
        if "," in raw:
            n_turns_config = [int(x.strip()) for x in raw.split(",")]
        else:
            n_turns_config = int(raw)
    else:
        n_turns_config = settings.get("n_turns", 3)

    turns_per_convo = resolve_turns(n_turns_config, n_convos)

    # mid_convo_topic_change: {topic: null|"random"|"stis", at_turn: null|int}
    mid_convo_cfg = settings.get("mid_convo_topic_change") or {}
    switch_topic = mid_convo_cfg.get("topic", None)
    switch_at_turn = mid_convo_cfg.get("at_turn", None)

    print("\n--- SETTINGS ---")
    print("Selection:", args.selection)
    print("Conversations:", n_convos)
    print("Turns per convo:", turns_per_convo)
    if switch_topic:
        at_turn_label = f"turn {switch_at_turn}" if switch_at_turn else "random turn"
        print(f"Mid-convo topic change: → '{switch_topic}' at {at_turn_label}")

    all_rows = []

    if args.selection == "manual":
        base_scenario = config.get("scenario")
        if not base_scenario:
            raise ValueError("No 'scenario' found in config.yaml")

        for i in range(n_convos):
            scenario = dict(base_scenario)
            convo_id = f"conv_{i+1}"
            print(f"\n--- SCENARIO {convo_id} ---")
            print(scenario)

            rows = run_conversation(
                scenario, turns_per_convo[i], convo_id,
                switch_topic=switch_topic,
                switch_at_turn=switch_at_turn,
                subcategory_distribution=config.get("distributions", {}).get("subcategory", {})
            )
            all_rows.extend(rows)

    elif args.selection == "random":
        distributions = config.get("distributions", {})
        if not distributions:
            raise ValueError("distributions required for random mode")

        for i in range(n_convos):
            scenario = {
                "high_level_category": weighted_choice(distributions["high_level_category"]),
                "subcategory": weighted_choice(distributions["subcategory"]),
                "tone": weighted_choice(distributions["tone"]),
                "barrier": weighted_choice(distributions["barrier"]),
                "gender": None,
                "age": None,
                "edge_case": None,
                "free_form": None,
            }

            convo_id = f"conv_{i+1}"
            print(f"\n--- SAMPLE SCENARIO {convo_id} ---")
            print(scenario)

            rows = run_conversation(
                scenario, turns_per_convo[i], convo_id,
                switch_topic=switch_topic,
                switch_at_turn=switch_at_turn,
                subcategory_distribution=distributions.get("subcategory", {})
            )
            all_rows.extend(rows)

    output_file = f"output_{args.selection}.csv"
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nSaved to {output_file}")


if __name__ == "__main__":
    main()
