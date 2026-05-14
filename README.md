# Synthetic Chatbot Runner

This repo generates synthetic multi-turn conversations between a GPT-simulated user and a chatbot API, then saves the results to CSV files. It also includes an evaluation notebook for checking how well generated conversations match the intended labels.

The main workflow is:

1. Configure a conversation scenario in `config.yaml`
2. Run `main.py` to generate synthetic conversations
3. Save the generated conversations as a CSV file
4. Use `evalcode_ge.ipynb` to evaluate the generated outputs

---

## Setup

Install dependencies:

```bash
pip install pyyaml requests openai pandas
```

Add API keys in `main.py`:

```python
OPENAI_API_KEY = ""
GIRL_EFFECT_TOKEN = ""
```

Do not commit real API keys to GitHub.

---

## Files

- `main.py`
- `config.yaml`
- `dia*_manual.csv`
- `evalcode_ge.ipynb`

### `main.py`

This is the main conversation generator.

It creates synthetic multi-turn conversations between:

- a GPT-generated simulated user
- the Girl Effect chatbot API

For each conversation, the script saves:

- conversation ID
- turn number
- user message
- bot response
- high-level category
- subcategory
- tone
- barrier
- gender
- age
- edge case
- free-form instruction
- topic switch information

### `config.yaml`

This file controls what kind of conversations get generated.

It includes:

- the manual scenario
- number of conversations
- number of turns
- optional mid-conversation topic switch
- probability distributions for random generation

Use this file to change the category, subcategory, tone, barrier, age, edge case, or free-form constraint.

### `dia*_manual.csv`

The `dia` CSV files are examples of generated outputs.

For example:

- `dia1_manual.csv`
- `dia2_manual.csv`
- `dia13_manual.csv`

These files show what the generated conversation data looks like after running `main.py`.

They are not the generator code. They are saved outputs from previous runs.

### `evalcode_ge.ipynb`

This notebook evaluates generated conversation files.

It checks things like:

- whether predicted subcategories match the labels
- whether tone matches
- whether barrier matches
- whether topic switches are detected correctly
- whether free-form constraints are detected
- whether edge cases are detected
- diversity of themes across conversations

The notebook produces evaluation result files such as:

- model evaluation results
- diversity results
- final summary metrics

---

## Run

Manual mode uses the fixed scenario from `config.yaml`:

```bash
python main.py --config config.yaml --selection manual
```

Optional overrides:

```bash
python main.py --config config.yaml --selection manual --n_convos 5 --n_turns 6
```

Random mode samples scenario values from the distributions in `config.yaml`:

```bash
python main.py --config config.yaml --selection random --n_convos 2 --n_turns 15
```

You can also pass a different number of turns per conversation:

```bash
python main.py --config config.yaml --selection manual --n_convos 3 --n_turns 4,5,6
```

---

## Config

Example `config.yaml`:

```yaml
scenario:
  high_level_category: srh
  subcategory: contraception
  tone: none_neutral_just_curious
  barrier: knowledge_barrier
  gender: female
  age: 18
  edge_case: null
  free_form: null

settings:
  n_convos: 3
  n_turns: 4
  mid_convo_topic_change:
    topic: null
    at_turn: null

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
    confused: 0.0001

  barrier:
    knowledge_barrier: 0.6661
    practical_barrier: 0.0165
    social_norms_external_barrier: 0.1045
    social_support_barrier: 0.1075
    internal_struggle_barrier: 0.1054
```

---

## What It Does

- Generates user messages using GPT
- Keeps user messages short and realistic
- Sends each user message to the chatbot API
- Runs multi-turn conversations
- Passes conversation history each turn
- Supports manual and random scenario generation
- Supports optional mid-conversation topic switches
- Stores all generated results in a CSV

---

## Output

Generated conversation results are saved to a CSV.

In the current script, the output file is set here:

```python
output_file = f"dia13_{args.selection}.csv"
```

Each row contains:

- `conversation_id`
- `turn`
- `user_message`
- `bot_response`
- `high_level_category`
- `subcategory`
- `tone`
- `barrier`
- `gender`
- `age`
- `edge_case`
- `free_form`
- `topic_switched_at`
- `original_subcategory`

---

## Evaluation

Use `evalcode_ge.ipynb` to evaluate generated files.

The evaluation notebook can:

- compare predicted labels against ground-truth labels
- calculate subcategory accuracy at the turn level
- calculate tone, barrier, topic switch, free-form, edge-case, and age matches
- extract themes from conversations
- calculate within-conversation diversity
- calculate between-conversation diversity
- save evaluation results to CSV files

Example evaluation outputs include:

- `eval_results13.csv`
- `diversity_results_13.csv`
- `theme_cache.json`

---

## Important Note About Saving Files

Before running the generator or evaluation notebook, update any output file names that will be saved.

This is important because existing files can be overwritten.

For example, in `main.py`, change this before running a new batch:

```python
output_file = f"dia13_{args.selection}.csv"
```

To something new, such as:

```python
output_file = f"dia14_{args.selection}.csv"
```

Also check the evaluation notebook for saved output files such as:

```python
eval_results13.csv
diversity_results_13.csv
theme_cache.json
```

Update these names before running a new evaluation so previous results are not overwritten.

---

## Suggested Workflow

1. Update `config.yaml` with the scenario you want to test.
2. Update the output CSV name in `main.py`.
3. Run `main.py`.
4. Open `evalcode_ge.ipynb`.
5. Update the notebook to read the new generated CSV file.
6. Update any saved evaluation file names.
7. Run the notebook.
8. Review the evaluation metrics and output CSVs.

---

## Notes

- `main.py` and `config.yaml` are the chat generation files.
- `dia*_manual.csv` files are examples of generated outputs.
- `evalcode_ge.ipynb` is for evaluating generated files.
- Manual mode uses the fixed scenario from `config.yaml`.
- Random mode samples scenario values from the distributions in `config.yaml`.
- Conversation history is passed each turn.
- Progress is printed in the terminal.
- Always rename output files before saving new runs.
- Be careful not to overwrite previous generated conversations or evaluation results.
- Keep API keys private and do not push them to GitHub.
