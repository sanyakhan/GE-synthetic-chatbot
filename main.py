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


#generate user message (GPT)
def generate_user_message(scenario, history):
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a realistic young user talking to a sexual health chatbot."},
            {"role": "user", "content": f"""
Scenario:
{scenario}

Conversation so far:
{history}

Respond as the USER:
- under 20 words
- tone: {scenario.get('tone')}
- topic: {scenario.get('subcategory')}
"""}
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
            "history": history,
            "use_stored_history": False
        },
        timeout=60
    )

    try:
        return response.json()
    except:
        return {"error": response.text, "status": response.status_code}


#run one conversation
def run_conversation(scenario, n_turns, convo_id):
    history = []
    rows = []

    print(f"\n=== Starting Conversation {convo_id} ===")

    for turn in range(n_turns):
        print(f"[{convo_id}] Turn {turn+1}/{n_turns}...")

        # user
        user_msg = generate_user_message(scenario, history)
        print("USER:", user_msg)

        history.append({"sender": "user", "text": user_msg})

        # bot
        bot_response = call_chatbot(user_msg, history)
        bot_msg = bot_response.get("message_text", f"ERROR: {bot_response}")

        print("BOT:", bot_msg)

        history.append({"sender": "bot", "text": bot_msg})

        # save row
        rows.append({
            "conversation_id": convo_id,
            "turn": turn + 1,
            "user_message": user_msg,
            "bot_response": bot_msg,
            "high_level_category": scenario.get("high_level_category"),
            "subcategory": scenario.get("subcategory"),
            "tone": scenario.get("tone"),
            "barrier": scenario.get("barrier"),
            "gender": scenario.get("gender"),
            "age": scenario.get("age"),
            "edge_case": scenario.get("edge_case")
        })

    return rows


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--selection", type=str, required=True, choices=["manual", "random"])
    parser.add_argument("--n_convos", type=int)
    parser.add_argument("--n_turns", type=int)

    args = parser.parse_args()

    # load config
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    # settings
    n_convos = args.n_convos or config.get("settings", {}).get("n_convos", 1)
    n_turns = args.n_turns or config.get("settings", {}).get("n_turns", 3)

    print("\n--- SETTINGS ---")
    print("Selection:", args.selection)
    print("Conversations:", n_convos)
    print("Turns:", n_turns)

    all_rows = []

    # manual
    if args.selection == "manual":
        scenario = config.get("scenario")

        if not scenario:
            raise ValueError("No 'scenario' found in config.yaml")

        print("\n--- SCENARIO ---")
        print(scenario)

        for i in range(n_convos):
            convo_id = f"conv_{i+1}"
            rows = run_conversation(scenario, n_turns, convo_id)
            all_rows.extend(rows)

    # random from weighted
    elif args.selection == "random":
        distributions = config.get("distributions", {})

    if not distributions:
        raise ValueError("distributions required for random mode")

    # sample one scenario
    scenario = {
        "high_level_category": weighted_choice(distributions["high_level_category"]),
        "subcategory": weighted_choice(distributions["subcategory"]),
        "tone": weighted_choice(distributions["tone"]),
        "barrier": weighted_choice(distributions["barrier"]),
        "gender": None,
        "age": None,
        "edge_case": None
    }

    print("\n--- SAMPLE SCENARIO (USED FOR ALL CONVERSATIONS) ---")
    print(scenario)

    # run convos of same scenario
    for i in range(n_convos):
        convo_id = f"conv_{i+1}"
        rows = run_conversation(scenario, n_turns, convo_id)
        all_rows.extend(rows)

    # save to csv (fill in file)
    with open("output2.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)

    print("\nSaved to output.csv")


if __name__ == "__main__":
    main()