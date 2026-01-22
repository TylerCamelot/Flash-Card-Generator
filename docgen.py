import os
import json
from typing import List, Dict, Any


def generate_flashcards_llm(
    study_text: str,
    num_cards: int = 15,
    difficulty: str = "Medium",
    model: str = "gpt-4.1-mini",
    api_key_env: str = "OPENAI_API_KEY",
    retry_on_json_failure: bool = True,
) -> List[Dict[str, Any]]:
    """
    Generate flashcards from study material using an LLM (OpenAI), enforcing JSON output.

    Output schema (strict):
      [
        {"question": "...", "answer": "...", "difficulty": "Easy|Medium|Hard"},
        ...
      ]

    Error handling:
      - ValueError for invalid inputs
      - RuntimeError for missing API key / missing SDK
      - Retries ONCE if JSON parsing fails (optional)
      - Raises a user-friendly RuntimeError if JSON is still invalid after retry
    """
    # -----------------------------
    # Validate inputs
    # -----------------------------
    if not isinstance(study_text, str) or not study_text.strip():
        raise ValueError("Please paste some study material before generating flashcards.")

    if not isinstance(num_cards, int) or not (1 <= num_cards <= 100):
        raise ValueError("Number of flashcards must be between 1 and 100.")

    if difficulty not in {"Easy", "Medium", "Hard"}:
        raise ValueError("Difficulty must be one of: Easy, Medium, Hard.")

    api_key = os.getenv(api_key_env, "").strip()
    if not api_key:
        raise RuntimeError(
            f"Missing API key. Please set {api_key_env} as an environment variable to use LLM mode."
        )

    # Lazy import so your app can still run without the dependency until needed
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:
        raise RuntimeError("OpenAI SDK not installed. Run: pip install openai") from e

    client = OpenAI(api_key=api_key)

    # -----------------------------
    # Prompting: enforce JSON-only + higher-quality answers
    # -----------------------------
    schema_hint = [
        {"question": "string", "answer": "string", "difficulty": "Easy|Medium|Hard"}
    ]

    system_msg = (
        "You are a helpful tutor that creates high-quality study flashcards.\n"
        "You MUST return valid JSON only, with no markdown, no backticks, and no extra text.\n"
        "Never output anything except JSON.\n"
        "If you cannot comply, return an empty JSON array: []."
    )

    user_msg = f"""
Create exactly {num_cards} flashcards from the study material below.

STRICT OUTPUT RULES:
- Output MUST be valid JSON ONLY (no markdown, no backticks, no commentary).
- Output must be a JSON array of objects matching this schema:
  {json.dumps(schema_hint, indent=2)}
- Each object MUST include: question, answer, difficulty.
- difficulty MUST be exactly one of: Easy, Medium, Hard.
- Questions must be specific (define a term, explain a concept, interpret a metric, compare ideas).
- Answers MUST be definition-style and must NOT simply repeat the question or quote the prompt.
- If a note is phrased as a mnemonic (e.g., “Of actual positives, how many did we catch?”),
  convert it into a definition card (e.g., Recall definition and/or formula if present).
- Keep answers concise (1–3 sentences). Include formulas only if present in the notes.

Target difficulty level: {difficulty}

STUDY_MATERIAL:
{study_text}
""".strip()

    def llm_call(messages: List[Dict[str, str]]) -> str:
        """Make a single LLM call and return the response content."""
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
        )
        return (resp.choices[0].message.content or "").strip()

    def _norm(s: str) -> str:
        """Normalize text for echo detection."""
        return " ".join((s or "").strip().lower().split())

    def parse_and_validate(json_text: str) -> List[Dict[str, Any]]:
        """
        Parse JSON and validate schema strictly.
        Also rejects low-quality 'echo' answers (answer ~= question).
        """
        if not json_text:
            raise RuntimeError("The AI returned an empty response. Please try again.")

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise e  # handled by retry logic upstream

        if not isinstance(data, list) or len(data) == 0:
            raise RuntimeError("The AI did not return any flashcards. Try increasing input detail or retry.")

        cleaned: List[Dict[str, Any]] = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise RuntimeError(f"Flashcard #{i+1} is not a valid object.")

            q = item.get("question")
            a = item.get("answer")
            d = item.get("difficulty")

            if not isinstance(q, str) or not q.strip():
                raise RuntimeError(f"Flashcard #{i+1} is missing a valid 'question'.")

            if not isinstance(a, str) or not a.strip():
                raise RuntimeError(f"Flashcard #{i+1} is missing a valid 'answer'.")

            if d not in {"Easy", "Medium", "Hard"}:
                raise RuntimeError(
                    f"Flashcard #{i+1} has invalid 'difficulty'. Must be Easy, Medium, or Hard."
                )

            # ---- Quality guardrail: prevent echo cards ----
            if _norm(q) == _norm(a):
                raise RuntimeError(
                    f"Flashcard #{i+1} appears to echo the question in the answer. Please regenerate."
                )

            cleaned.append(
                {"question": q.strip(), "answer": a.strip(), "difficulty": d}
            )

        return cleaned

    # -----------------------------
    # Attempt 1: normal generation
    # -----------------------------
    try:
        content = llm_call(
            [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ]
        )
        return parse_and_validate(content)

    except json.JSONDecodeError:
        if not retry_on_json_failure:
            raise RuntimeError(
                "The AI returned invalid JSON. Please try again (or reduce input size)."
            )

        # -----------------------------
        # Attempt 2 (Retry): "Fix JSON only"
        # -----------------------------
        fix_system = (
            "You are a JSON repair tool.\n"
            "Return ONLY valid JSON with no extra text.\n"
            "Do not add new flashcards unless required to match the schema.\n"
        )

        fix_user = f"""
The following output is supposed to be a JSON array of flashcards but is invalid.
Fix it and return ONLY valid JSON.

Required schema:
{json.dumps(schema_hint, indent=2)}

BROKEN_OUTPUT:
{content}
""".strip()

        try:
            fixed = llm_call(
                [
                    {"role": "system", "content": fix_system},
                    {"role": "user", "content": fix_user},
                ]
            )
            return parse_and_validate(fixed)

        except json.JSONDecodeError:
            raise RuntimeError(
                "Flashcard generation failed because the AI returned invalid JSON twice. "
                "Please try again, shorten the input text, or switch to a different model."
            )

    except RuntimeError:
        # Re-raise user-friendly validation errors (including echo detection)
        raise

    except Exception as e:
        # Catch-all for network/model issues
        raise RuntimeError(f"LLM request failed: {e}")
