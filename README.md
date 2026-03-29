# Synthetic Chatbot Runner

This script generates synthetic multi-turn conversations between a GPT-simulated user and a chatbot API, then saves results to a CSV.

---

## Setup

Install dependencies:

pip install pyyaml requests openai

---

## Files

- main.py
- config.yaml

---

## Run

Manual mode (uses fixed scenario from config):

python main.py --config config.yaml --selection manual

Optional overrides:

python main.py --config config.yaml --selection manual --n_convos 5 --n_turns 6

Random mode (samples scenario from distributions):

python main.py --config config.yaml --selection random --n_convos 2 --n_turns 15

---

## Config

Example config.yaml:

scenario:
  high_level_category: srh
  subcategory: contraception
  tone: shy
  barrier: knowledge_barrier
  gender: female
  age: 18
  edge_case: null

settings:
  n_convos: 3
  n_turns: 4

distributions:
  high_level_category:
    srh: 0.7483
    mwb: 0.2469
    both: 0.0048

  subcategory:
    puberty_and_body_changes: 0.1299
    menstruation_and_cycle_issues: 0.0577
    pregnancy: 0.1607
    abortion: 0.0061
    contraception: 0.0428
    stis: 0.0455
    hiv_aids: 0.0196
    intimate_relationships_and_consent: 0.5301
    srh_services: 0.0076

  tone:
    none_neutral_just_curious: 0.7669
    fear_shame_stigma: 0.0648
    anxiety_overwhelm: 0.0880
    positive_health_seeking: 0.0804

  barrier:
    knowledge_barrier: 0.6661
    practical_barrier: 0.0165
    social_norms_external_barrier: 0.1045
    social_support_barrier: 0.1075
    internal_struggle_barrier: 0.1054

---

## What It Does

- Generates user messages using GPT (under 20 words)
- Sends messages to chatbot API
- Runs multi-turn conversations
- Stores all results in a CSV

---

## Output

Results are saved to:

output2.csv

Each row contains:

- conversation_id
- turn
- user_message
- bot_response
- high_level_category
- subcategory
- tone
- barrier
- gender
- age
- edge_case

---

## Notes

- Random mode samples ONE scenario and reuses it across all conversations
- Conversation history is passed each turn
- Progress is printed in the terminal