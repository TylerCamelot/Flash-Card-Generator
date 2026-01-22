# app.py
"""
Study Flashcard Generator (Streamlit)

Features
- Paste study material (text)
- Generate flashcards via LLM (OpenAI) OR fallback Mock Mode (no API key required)
- Review/edit/delete flashcards (stored in st.session_state)
- Quiz mode: one card at a time in random order + self-grading + final score + missed questions
- Export flashcards to Anki (TSV) or Quizlet (CSV)

Run
  streamlit run app.py

Notes
- LLM generation uses generate_flashcards_llm() from docgen.py
- Mock Mode ensures the app remains functional even without an API key
"""

from __future__ import annotations

import csv
import io
import os
import random
import re
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv

from docgen import generate_flashcards_llm

load_dotenv()

# -----------------------------
# Constants / Config
# -----------------------------
API_KEY_ENV = "OPENAI_API_KEY"
DIFFICULTY_OPTIONS = ["Easy", "Medium", "Hard"]
PROVIDER_OPTIONS = ["Auto (LLM if available)", "LLM Only", "Mock Mode"]


# -----------------------------
# Session State Helpers
# -----------------------------
def ensure_flashcard_state() -> None:
    """Ensure flashcard storage exists in session_state."""
    st.session_state.setdefault("flashcards", [])


def ensure_quiz_state() -> None:
    """Ensure quiz-related state exists in session_state."""
    st.session_state.setdefault("quiz_active", False)
    st.session_state.setdefault("quiz_order", [])
    st.session_state.setdefault("quiz_pos", 0)
    st.session_state.setdefault("quiz_correct", 0)
    st.session_state.setdefault("quiz_incorrect", [])
    st.session_state.setdefault("reveal_answer", False)


def reset_quiz_state() -> None:
    """Reset quiz state to a clean 'not running' condition."""
    st.session_state["quiz_active"] = False
    st.session_state["quiz_order"] = []
    st.session_state["quiz_pos"] = 0
    st.session_state["quiz_correct"] = 0
    st.session_state["quiz_incorrect"] = []
    st.session_state["reveal_answer"] = False


def llm_available(api_key_env: str = API_KEY_ENV) -> bool:
    """Return True if an LLM API key is detected in environment variables."""
    return bool(os.getenv(api_key_env, "").strip())


# -----------------------------
# Quality Filtering (prevents "echo" cards)
# -----------------------------
def _norm(s: str) -> str:
    """Normalize text for comparisons."""
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def is_low_quality_card(card: Dict[str, Any]) -> bool:
    """
    Heuristics to detect low-quality cards:
    - missing question/answer
    - answer echoes question
    - very short answer
    - answer is just a short substring of the question
    """
    q = _norm(card.get("question", ""))
    a = _norm(card.get("answer", ""))
    if not q or not a:
        return True
    if a == q:
        return True
    if len(a) < 12:
        return True
    if a in q and len(a) < 40:
        return True
    return False


def quality_filter_cards(
    cards: List[Dict[str, Any]],
    allow_llm_fix: bool,
    model_name: str,
    difficulty: str,
) -> List[Dict[str, Any]]:
    """
    Fix/filter low-quality cards BEFORE showing them to the user.
    - Applies heuristic fixes for common echo patterns
    - Optionally uses the LLM to repair ONLY the bad cards (fast/cheap)
    """
    if not cards:
        return cards

    bad = [c for c in cards if is_low_quality_card(c)]
    good = [c for c in cards if not is_low_quality_card(c)]

    # Heuristic fixes first (works even without API)
    fixed_bad: List[Dict[str, Any]] = []
    for c in bad:
        q = (c.get("question") or "").strip()
        a = (c.get("answer") or "").strip()

        # If answer equals question, convert to definition-style stub
        if _norm(q) == _norm(a):
            c["answer"] = f"Definition/Explanation: {a}"

        # If answer is very short, add a hint to encourage meaning
        if len((c.get("answer") or "").strip()) < 20:
            c["answer"] = (c.get("answer") or "").strip() + " (expand based on the notes above)"

        # Always enforce difficulty key
        c["difficulty"] = c.get("difficulty") or difficulty

        fixed_bad.append(c)

    # Optional: LLM repair for only the bad cards (if available + enabled)
    if allow_llm_fix and llm_available() and fixed_bad:
        try:
            repair_text = (
                "Rewrite these flashcards so answers are definition-style, not echoes, and concise.\n"
                "Return corrected flashcards.\n\n"
            )
            repair_text += "\n".join(
                [f"Q: {c.get('question','')}\nA: {c.get('answer','')}\n" for c in fixed_bad]
            )

            repaired = generate_flashcards_llm(
                study_text=repair_text,
                num_cards=len(fixed_bad),
                difficulty=difficulty,
                model=model_name,
            )

            return good + repaired
        except Exception:
            # If repair fails, keep heuristic fixes
            return good + fixed_bad

    return good + fixed_bad


# -----------------------------
# Mock Flashcard Generator (Fallback) - FURTHER IMPROVED
# -----------------------------
def mock_generate_flashcards(
    study_text: str,
    num_cards: int = 15,
    difficulty: str = "Medium",
) -> List[Dict[str, Any]]:
    """
    Further-improved Mock Mode generator (no LLM).

    Enhancements:
    - Extracts Term–Definition pairs from more formats: ':', '=', '-', '–', '—'
    - Supports Concept/Definition and Concept/Explanation multi-line patterns
    - Detects definitional language and creates definition-style Q/A
    - Detects formulas and builds formula-focused questions
    - Better metric mnemonic detection (recall/precision/accuracy/F1/AUC/ROC)
    - Difficulty affects question style (Easy/Medium/Hard)

    Raises:
        ValueError: if study_text is empty
    """
    text = (study_text or "").strip()
    if not text:
        raise ValueError("Please paste some study material before generating flashcards.")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # -----------------------------
    # 1) Extract explicit term-definition pairs
    # -----------------------------
    pairs: List[Dict[str, str]] = []

    # Term: definition
    term_colon = re.compile(r"^([A-Za-z][A-Za-z0-9\s\-_]{1,60})\s*:\s+(.{10,})$")
    # Term = formula/definition
    term_eq = re.compile(r"^([A-Za-z][A-Za-z0-9\s\-_]{1,60})\s*=\s*(.{6,})$")
    # Term - definition (including en/em dash)
    term_dash = re.compile(r"^([A-Za-z][A-Za-z0-9\s\-_]{1,60})\s*[-–—]\s+(.{10,})$")

    for ln in lines:
        for rx in (term_colon, term_eq, term_dash):
            m = rx.match(ln)
            if m:
                term = m.group(1).strip()
                definition = m.group(2).strip()
                pairs.append({"term": term, "definition": definition})
                break

    # Also support:
    # Concept: X
    # Definition: Y  (or Explanation:)
    i = 0
    while i < len(lines) - 1:
        if lines[i].lower().startswith(("concept:", "term:", "metric:")):
            term = lines[i].split(":", 1)[1].strip()
            definition = ""
            j = i + 1
            while j < len(lines) and j <= i + 4:
                if lines[j].lower().startswith(("definition:", "explanation:")):
                    definition = lines[j].split(":", 1)[1].strip()
                    break
                j += 1
            if term and definition:
                pairs.append({"term": term, "definition": definition})
                i = j + 1
                continue
        i += 1

    # Deduplicate pairs by term
    seen_terms = set()
    uniq_pairs = []
    for p in pairs:
        key = p["term"].lower()
        if key not in seen_terms:
            seen_terms.add(key)
            uniq_pairs.append(p)
    pairs = uniq_pairs

    # -----------------------------
    # 2) Build sentence-ish chunks
    # -----------------------------
    chunks: List[str] = []
    for ln in lines:
        parts = re.split(r"(?<=[.!?])\s+", ln)
        for p in parts:
            p = p.strip()
            if len(p) >= 20:
                chunks.append(p)

    # Deduplicate chunks
    seen = set()
    uniq_chunks = []
    for c in chunks:
        k = c.lower()
        if k not in seen:
            seen.add(k)
            uniq_chunks.append(c)
    chunks = uniq_chunks

    # -----------------------------
    # 3) Helpers to detect definitions / formulas / metrics
    # -----------------------------
    def looks_like_definition(s: str) -> bool:
        s2 = s.lower()
        return any(kw in s2 for kw in [" is ", " are ", " refers to ", " means ", " defined as ", " occurs when "])

    def extract_term_from_definition(s: str) -> str:
        # crude: "X is ..." -> X
        m = re.match(
            r"^([A-Za-z][A-Za-z0-9\s\-_]{1,40})\s+(is|are|refers to|means|occurs when)\b",
            s.strip(),
            flags=re.I,
        )
        return m.group(1).strip() if m else ""

    def detect_formula(snippet: str) -> bool:
        # detect "=" or fraction structure with common tokens
        s = snippet
        return ("=" in s) or ("/" in s and any(tok in s.lower() for tok in ["tp", "fp", "tn", "fn"]))

    def detect_metric(snippet: str) -> str:
        s = snippet.lower()
        if ("actual positives" in s or "actual positive" in s) and ("catch" in s or "caught" in s):
            return "Recall"
        if ("predicted positives" in s or "predicted positive" in s) and ("actually positive" in s or "correct" in s):
            return "Precision"
        if "confusion matrix" in s or ("tp" in s and "tn" in s and "fp" in s and "fn" in s):
            return "Confusion Matrix"
        if "f1" in s and ("precision" in s and "recall" in s):
            return "F1 Score"
        if "accuracy" in s and ("tp" in s or "tn" in s):
            return "Accuracy"
        if "roc" in s:
            return "ROC Curve"
        if "auc" in s or "area under" in s:
            return "AUC"
        return ""

    # Difficulty-based question styles
    if difficulty == "Easy":
        generic_prompts = [
            "Define:",
            "What is:",
            "What does this term mean:",
            "Give a brief definition of:",
        ]
    elif difficulty == "Medium":
        generic_prompts = [
            "Explain the following concept:",
            "Why is this important:",
            "How would you describe:",
            "Summarize this idea:",
        ]
    else:  # Hard
        generic_prompts = [
            "Compare this concept to a related idea and explain the difference:",
            "Apply this concept to a real scenario—what would you do and why?",
            "What is a common pitfall or edge case related to this concept?",
            "What tradeoff is implied here and why?",
        ]

    # -----------------------------
    # 4) Build cards
    # -----------------------------
    cards: List[Dict[str, Any]] = []

    # Prefer explicit term/definition pairs first
    for p in pairs:
        if len(cards) >= num_cards:
            break
        term = p["term"]
        definition = p["definition"]

        if detect_formula(definition) and len(term) <= 35:
            q = f"What is the formula for {term}?"
            a = definition
        else:
            q = f"What is {term}?"
            a = definition

        cards.append({"question": q, "answer": a, "difficulty": difficulty})

    # Then create cards from chunks (definitions, metrics, or generic)
    random.shuffle(chunks)
    for snippet in chunks:
        if len(cards) >= num_cards:
            break

        metric = detect_metric(snippet)
        if metric:
            cards.append({"question": f"What does {metric} mean?", "answer": snippet, "difficulty": difficulty})
            continue

        if looks_like_definition(snippet):
            term = extract_term_from_definition(snippet)
            if term:
                cards.append({"question": f"What is {term}?", "answer": snippet, "difficulty": difficulty})
                continue

        # Generic fallback
        q = f"{random.choice(generic_prompts)}\n\n{snippet}"
        cards.append({"question": q, "answer": snippet, "difficulty": difficulty})

    # Pad if needed
    while len(cards) < num_cards and chunks:
        snippet = random.choice(chunks)
        q = f"{random.choice(generic_prompts)}\n\n{snippet}"
        cards.append({"question": q, "answer": snippet, "difficulty": difficulty})

    return cards


# -----------------------------
# CSV Export Helpers
# -----------------------------
def flashcards_to_anki_tsv(cards: List[Dict[str, Any]]) -> bytes:
    """Anki-friendly TSV: Front, Back, Tags (difficulty as tag)."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    writer.writerow(["Front", "Back", "Tags"])

    for c in cards:
        front = (c.get("question", "") or "").strip()
        back = (c.get("answer", "") or "").strip()
        diff = (c.get("difficulty", "") or "").strip()
        tags = diff.replace(" ", "_") if diff else ""
        writer.writerow([front, back, tags])

    return output.getvalue().encode("utf-8")


def flashcards_to_quizlet_csv(cards: List[Dict[str, Any]]) -> bytes:
    """Quizlet-friendly CSV: Term, Definition."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=",", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    writer.writerow(["Term", "Definition"])

    for c in cards:
        term = (c.get("question", "") or "").strip()
        definition = (c.get("answer", "") or "").strip()
        writer.writerow([term, definition])

    return output.getvalue().encode("utf-8")


def render_export_section() -> None:
    """Render download buttons for exporting flashcards."""
    ensure_flashcard_state()
    cards = st.session_state["flashcards"]
    if not cards:
        return

    st.subheader("5) Export Flashcards")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Download Anki TSV (Front/Back/Tags)",
            data=flashcards_to_anki_tsv(cards),
            file_name="flashcards_anki.tsv",
            mime="text/tab-separated-values",
            help="Import into Anki using TSV. Tags include difficulty.",
        )
    with col2:
        st.download_button(
            label="⬇️ Download Quizlet CSV (Term/Definition)",
            data=flashcards_to_quizlet_csv(cards),
            file_name="flashcards_quizlet.csv",
            mime="text/csv",
            help="Import into Quizlet as Term/Definition pairs.",
        )


# -----------------------------
# Flashcard Review / Editor UI
# -----------------------------
def flashcard_review_editor() -> None:
    """Editable flashcard review UI (edit/delete) that persists to session_state."""
    ensure_flashcard_state()
    ensure_quiz_state()

    cards = st.session_state["flashcards"]
    if not cards:
        st.info("No flashcards yet. Generate some to review them here.")
        return

    st.subheader("3) Review & Edit Flashcards")

    col_a, col_b, col_c = st.columns([1, 1, 2])
    with col_a:
        st.caption(f"Cards: {len(cards)}")
    with col_b:
        if st.button("🧹 Clear all cards", type="secondary"):
            st.session_state["flashcards"] = []
            reset_quiz_state()
            st.rerun()
    with col_c:
        st.caption("Tip: edit inline, then mark cards and click “Delete selected”.")

    delete_indices: List[int] = []

    for i, card in enumerate(cards):
        title = (card.get("question", "") or "").strip()
        short_title = title[:60] + ("..." if len(title) > 60 else "")

        with st.expander(f"Flashcard {i + 1}: {short_title}", expanded=(i == 0)):
            q_key = f"q_{i}"
            a_key = f"a_{i}"
            d_key = f"d_{i}"
            del_key = f"del_{i}"

            st.session_state.setdefault(q_key, card.get("question", ""))
            st.session_state.setdefault(a_key, card.get("answer", ""))
            st.session_state.setdefault(d_key, card.get("difficulty", "Medium"))
            st.session_state.setdefault(del_key, False)

            question = st.text_area("Question", key=q_key, height=80)
            answer = st.text_area("Answer", key=a_key, height=100)
            difficulty_val = st.selectbox("Difficulty", DIFFICULTY_OPTIONS, key=d_key)

            st.checkbox("Mark for deletion", key=del_key)

            st.session_state["flashcards"][i] = {
                "question": (question or "").strip(),
                "answer": (answer or "").strip(),
                "difficulty": difficulty_val,
            }

            if st.session_state[del_key]:
                delete_indices.append(i)

    if st.button("🗑️ Delete selected", disabled=(len(delete_indices) == 0)):
        to_delete = set(delete_indices)
        st.session_state["flashcards"] = [
            c for idx, c in enumerate(st.session_state["flashcards"]) if idx not in to_delete
        ]
        reset_quiz_state()
        st.rerun()


# -----------------------------
# Quiz Mode
# -----------------------------
def start_quiz() -> None:
    """Start a quiz with randomized order."""
    ensure_flashcard_state()
    ensure_quiz_state()

    n = len(st.session_state["flashcards"])
    if n == 0:
        st.warning("You need flashcards before you can start a quiz.")
        return

    order = list(range(n))
    random.shuffle(order)

    st.session_state["quiz_active"] = True
    st.session_state["quiz_order"] = order
    st.session_state["quiz_pos"] = 0
    st.session_state["quiz_correct"] = 0
    st.session_state["quiz_incorrect"] = []
    st.session_state["reveal_answer"] = False


def quiz_mode() -> None:
    """Quiz UI: one card at a time + self-grading + final recap."""
    ensure_flashcard_state()
    ensure_quiz_state()

    cards = st.session_state["flashcards"]
    order = st.session_state["quiz_order"]
    pos = st.session_state["quiz_pos"]

    st.subheader("4) Quiz Mode")

    if st.session_state["quiz_active"] and len(order) != len(cards):
        st.warning("Flashcards changed since the quiz started. Please restart the quiz.")
        reset_quiz_state()
        return

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🎲 Start Quiz", type="primary", disabled=(len(cards) == 0)):
            start_quiz()
            st.rerun()
    with col2:
        if st.button("🔄 Restart Quiz", disabled=(len(cards) == 0)):
            start_quiz()
            st.rerun()
    with col3:
        if st.button("🛑 End Quiz", disabled=not st.session_state["quiz_active"]):
            reset_quiz_state()
            st.rerun()

    if not st.session_state["quiz_active"]:
        st.info("Start a quiz to practice. You’ll see one flashcard at a time and self-grade.")
        return

    total = len(order)

    if pos >= total:
        correct = st.session_state["quiz_correct"]
        pct = (correct / total) * 100 if total else 0.0
        st.success(f"Quiz Complete! Score: {correct}/{total} ({pct:.1f}%)")

        missed = st.session_state["quiz_incorrect"]
        if missed:
            st.markdown("### ❌ Missed Questions")
            for i, miss in enumerate(missed, start=1):
                label = miss["question"][:80] + ("..." if len(miss["question"]) > 80 else "")
                with st.expander(f"Missed {i}: {label}"):
                    st.markdown(f"**Question:** {miss['question']}")
                    st.markdown(f"**Correct Answer:** {miss['answer']}")
                    if miss.get("your_answer"):
                        st.markdown(f"**Your Answer (optional):** {miss['your_answer']}")
                    st.caption(f"Difficulty: {miss.get('difficulty', '')}")
        else:
            st.balloons()
            st.info("Perfect score — no missed questions!")
        return

    card = cards[order[pos]]
    q = card.get("question", "")
    a = card.get("answer", "")
    d = card.get("difficulty", "Medium")

    st.progress(pos / total)
    st.caption(f"Question {pos + 1} of {total} • Difficulty: {d}")
    st.markdown(f"### {q}")

    user_answer = st.text_area("Your answer (optional)", key=f"ans_{pos}", height=100)

    if not st.session_state["reveal_answer"]:
        if st.button("👀 Reveal Answer"):
            st.session_state["reveal_answer"] = True
            st.rerun()
        return

    st.markdown("#### ✅ Correct Answer")
    st.markdown(a)

    col_ok, col_no = st.columns(2)
    with col_ok:
        if st.button("✅ Correct"):
            st.session_state["quiz_correct"] += 1
            st.session_state["quiz_pos"] += 1
            st.session_state["reveal_answer"] = False
            st.rerun()

    with col_no:
        if st.button("❌ Incorrect"):
            st.session_state["quiz_incorrect"].append(
                {
                    "question": q,
                    "answer": a,
                    "difficulty": d,
                    "your_answer": (user_answer or "").strip(),
                }
            )
            st.session_state["quiz_pos"] += 1
            st.session_state["reveal_answer"] = False
            st.rerun()


# -----------------------------
# LLM / Generation Orchestration
# -----------------------------
def generate_cards(
    provider: str,
    study_text: str,
    num_cards: int,
    difficulty: str,
    model_name: str,
) -> List[Dict[str, Any]]:
    """Generate flashcards using LLM or Mock Mode with robust error handling."""
    if not (study_text or "").strip():
        raise ValueError("Please paste some study material before generating flashcards.")

    if provider == "LLM Only":
        use_llm = True
    elif provider == "Mock Mode":
        use_llm = False
    else:
        use_llm = llm_available()

    if use_llm:
        if not llm_available():
            raise RuntimeError(
                f"LLM mode selected but no API key found. Set {API_KEY_ENV} or switch Provider to Mock Mode."
            )
        return generate_flashcards_llm(
            study_text=study_text,
            num_cards=num_cards,
            difficulty=difficulty,
            model=model_name,
        )

    return mock_generate_flashcards(study_text=study_text, num_cards=num_cards, difficulty=difficulty)


# -----------------------------
# Streamlit App UI (Main)
# -----------------------------
st.set_page_config(page_title="Study Flashcard Generator", page_icon="📚", layout="wide")

st.title("📚 Study Flashcard Generator")
st.caption("Paste study material, generate flashcards (LLM or Mock Mode), review them, quiz yourself, and export.")

ensure_flashcard_state()
ensure_quiz_state()

with st.sidebar:
    st.header("Configuration")

    num_cards = st.slider(
        "Number of flashcards",
        min_value=5,
        max_value=50,
        value=15,
        step=1,
        help="How many flashcards to generate from your study material.",
    )

    difficulty = st.selectbox(
        "Difficulty",
        DIFFICULTY_OPTIONS,
        index=1,
        help="Controls how challenging the generated questions are.",
    )

    st.markdown("---")
    st.subheader("Generation Mode")

    provider = st.selectbox(
        "Provider",
        PROVIDER_OPTIONS,
        index=0,
        help="Auto uses LLM if an API key is set, otherwise uses Mock Mode.",
    )

    st.subheader("LLM Settings")
    model_name = st.text_input("Model name", value="gpt-4.1-mini")
    st.caption(f"LLM API key detected: **{llm_available()}**")

st.subheader("1) Paste study material")
study_text = st.text_area(
    "Study material",
    height=250,
    placeholder="Paste your notes, textbook excerpts, or lecture summaries here...",
)

st.subheader("2) Generate flashcards")
if st.button("🚀 Generate Flashcards", type="primary"):
    try:
        cards = generate_cards(
            provider=provider,
            study_text=study_text,
            num_cards=num_cards,
            difficulty=difficulty,
            model_name=model_name,
        )

        # Quality filter step (auto-fix weak cards BEFORE showing them)
        cards = quality_filter_cards(
            cards=cards,
            allow_llm_fix=(provider != "Mock Mode"),
            model_name=model_name,
            difficulty=difficulty,
        )

        st.session_state["flashcards"] = cards
        reset_quiz_state()

        mode_used = "LLM" if (provider == "LLM Only" or (provider.startswith("Auto") and llm_available())) else "MOCK"
        st.success(f"Generated {len(cards)} flashcards. (Mode: {mode_used})")

    except ValueError as e:
        st.warning(str(e))
    except Exception as e:
        st.error(f"Generation failed: {e}")

if st.session_state["flashcards"]:
    flashcard_review_editor()
    render_export_section()

quiz_mode()
