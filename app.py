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

from docgen import generate_flashcards_llm


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
# Mock Flashcard Generator (Fallback)
# -----------------------------
def mock_generate_flashcards(
    study_text: str,
    num_cards: int = 15,
    difficulty: str = "Medium",
) -> List[Dict[str, Any]]:
    """
    Generate simple flashcards without an LLM.

    Heuristic approach:
    - Split text into sentence-like chunks (including bullet lines)
    - Turn each chunk into a simple Q/A card
    - Difficulty is assigned as provided to keep UI consistent

    Raises:
        ValueError: if study_text is empty
    """
    text = (study_text or "").strip()
    if not text:
        raise ValueError("Please paste some study material before generating flashcards.")

    # Break input into sentence-ish chunks for card creation
    chunks: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"(?<=[.!?])\s+", line)
        for p in parts:
            p = p.strip()
            if p and len(p) >= 20:  # ignore tiny fragments
                chunks.append(p)

    if not chunks:
        # Last resort: use a slice of the full text
        chunks = [text[:250]]

    # Deduplicate while preserving order
    seen = set()
    uniq: List[str] = []
    for c in chunks:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    chunks = uniq

    # Randomize selection and cap to requested count
    random.shuffle(chunks)
    chunks = chunks[: max(1, min(num_cards, len(chunks)))]

    q_templates = [
        "Explain the following concept:",
        "In your own words, what does this mean?",
        "Summarize this idea:",
        "What is the key takeaway from this statement?",
    ]

    cards: List[Dict[str, Any]] = []
    for snippet in chunks:
        q = f"{random.choice(q_templates)}\n\n{snippet}"
        a = snippet
        cards.append({"question": q, "answer": a, "difficulty": difficulty})

    # Pad up to num_cards by reusing snippets with a different template
    while len(cards) < num_cards and chunks:
        snippet = random.choice(chunks)
        q = f"What does this refer to?\n\n{snippet}"
        cards.append({"question": q, "answer": snippet, "difficulty": difficulty})

    return cards


# -----------------------------
# CSV Export Helpers
# -----------------------------
def flashcards_to_anki_tsv(cards: List[Dict[str, Any]]) -> bytes:
    """
    Anki-friendly export: TAB-delimited with columns:
      Front<TAB>Back<TAB>Tags

    We store difficulty as a tag (e.g., Easy/Medium/Hard).
    """
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
    """
    Quizlet-friendly export: comma-delimited with columns:
      Term,Definition
    """
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
    """
    Editable flashcard review UI:
    - Edit question/answer/difficulty inline
    - Mark cards for deletion
    - Clear all cards
    - Persist edits to st.session_state["flashcards"]
    """
    ensure_flashcard_state()
    ensure_quiz_state()

    cards = st.session_state["flashcards"]
    if not cards:
        st.info("No flashcards yet. Generate some to review them here.")
        return

    st.subheader("3) Review & Edit Flashcards")

    # Basic actions
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
        # Short title for expander label
        title = (card.get("question", "") or "").strip()
        short_title = title[:60] + ("..." if len(title) > 60 else "")

        with st.expander(f"Flashcard {i + 1}: {short_title}", expanded=(i == 0)):
            # Use unique keys per index so Streamlit can persist widget states
            q_key = f"q_{i}"
            a_key = f"a_{i}"
            d_key = f"d_{i}"
            del_key = f"del_{i}"

            # Initialize widget defaults once
            st.session_state.setdefault(q_key, card.get("question", ""))
            st.session_state.setdefault(a_key, card.get("answer", ""))
            st.session_state.setdefault(d_key, card.get("difficulty", "Medium"))
            st.session_state.setdefault(del_key, False)

            # Editable fields
            question = st.text_area("Question", key=q_key, height=80)
            answer = st.text_area("Answer", key=a_key, height=100)
            difficulty_val = st.selectbox("Difficulty", DIFFICULTY_OPTIONS, key=d_key)

            # Delete toggle
            st.checkbox("Mark for deletion", key=del_key)

            # Write changes back to session cards (live update)
            st.session_state["flashcards"][i] = {
                "question": (question or "").strip(),
                "answer": (answer or "").strip(),
                "difficulty": difficulty_val,
            }

            if st.session_state[del_key]:
                delete_indices.append(i)

    # Delete selected (post-loop to avoid index shifting)
    if st.button("🗑️ Delete selected", disabled=(len(delete_indices) == 0)):
        to_delete = set(delete_indices)
        st.session_state["flashcards"] = [
            c for idx, c in enumerate(st.session_state["flashcards"]) if idx not in to_delete
        ]
        # Editing/deleting changes indices—reset quiz to avoid mismatches
        reset_quiz_state()
        st.rerun()


# -----------------------------
# Quiz Mode
# -----------------------------
def start_quiz() -> None:
    """
    Start a new quiz with a randomized order of current flashcards.

    If no flashcards exist, show a warning and do nothing.
    """
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
    """
    Quiz UI:
    - Show one card at a time
    - User can type an answer (optional) and then reveal the answer
    - Self-grade correct/incorrect
    - Track score and show missed questions at the end
    """
    ensure_flashcard_state()
    ensure_quiz_state()

    cards = st.session_state["flashcards"]
    order = st.session_state["quiz_order"]
    pos = st.session_state["quiz_pos"]

    st.subheader("4) Quiz Mode")

    # Invalid user action handling: if cards changed mid-quiz, reset quiz state
    if st.session_state["quiz_active"] and len(order) != len(cards):
        st.warning("Flashcards changed since the quiz started. Please restart the quiz.")
        reset_quiz_state()
        return

    # Controls
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

    # Finished?
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

    # Current card
    idx = order[pos]
    card = cards[idx]

    q = card.get("question", "")
    a = card.get("answer", "")
    d = card.get("difficulty", "Medium")

    # Progress and question
    st.progress(pos / total)
    st.caption(f"Question {pos + 1} of {total} • Difficulty: {d}")
    st.markdown(f"### {q}")

    # Optional typed answer (self-grading keeps demo simple and robust)
    user_answer = st.text_area("Your answer (optional)", key=f"ans_{pos}", height=100)

    # Reveal answer toggle
    if not st.session_state["reveal_answer"]:
        if st.button("👀 Reveal Answer"):
            st.session_state["reveal_answer"] = True
            st.rerun()
        return

    st.markdown("#### ✅ Correct Answer")
    st.markdown(a)

    # Self-grade
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
    """
    Generate flashcards using LLM or Mock Mode with robust error handling.

    Raises:
        ValueError: invalid/empty input
        RuntimeError: LLM-related failures (API missing or request failure)
    """
    # Validate user input early (error handling requirement)
    if not (study_text or "").strip():
        raise ValueError("Please paste some study material before generating flashcards.")

    # Determine generator
    if provider == "LLM Only":
        use_llm = True
    elif provider == "Mock Mode":
        use_llm = False
    else:
        # Auto mode
        use_llm = llm_available()

    # Generate
    if use_llm:
        # If API key missing, surface a friendly message instead of crashing
        if not llm_available():
            raise RuntimeError(
                f"LLM mode selected but no API key found. "
                f"Set {API_KEY_ENV} or switch Provider to Mock Mode."
            )

        # This call can raise (API failures, invalid JSON, etc.) and will be caught in UI
        return generate_flashcards_llm(
            study_text=study_text,
            num_cards=num_cards,
            difficulty=difficulty,
            model=model_name,
        )

    # Mock Mode always works
    return mock_generate_flashcards(
        study_text=study_text,
        num_cards=num_cards,
        difficulty=difficulty,
    )


# -----------------------------
# Streamlit App UI (Main)
# -----------------------------
st.set_page_config(page_title="Study Flashcard Generator", page_icon="📚", layout="wide")

st.title("📚 Study Flashcard Generator")
st.caption("Paste study material, generate flashcards (LLM or Mock Mode), review them, quiz yourself, and export.")

# Ensure state exists
ensure_flashcard_state()
ensure_quiz_state()

# Sidebar controls
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

# Input section
st.subheader("1) Paste study material")
study_text = st.text_area(
    "Study material",
    height=250,
    placeholder="Paste your notes, textbook excerpts, or lecture summaries here...",
)

# Generate section
st.subheader("2) Generate flashcards")
if st.button("🚀 Generate Flashcards", type="primary"):
    try:
        # Generate cards (handles empty input + provider logic)
        cards = generate_cards(
            provider=provider,
            study_text=study_text,
            num_cards=num_cards,
            difficulty=difficulty,
            model_name=model_name,
        )

        # Store for downstream UI (review/quiz/export)
        st.session_state["flashcards"] = cards

        # Any time we regenerate, reset quiz to avoid index mismatches
        reset_quiz_state()

        mode_used = "LLM" if (provider == "LLM Only" or (provider.startswith("Auto") and llm_available())) else "MOCK"
        st.success(f"Generated {len(cards)} flashcards. (Mode: {mode_used})")

    except ValueError as e:
        # Friendly input errors
        st.warning(str(e))
    except Exception as e:
        # API failures / unexpected errors
        st.error(f"Generation failed: {e}")

# Review + Export + Quiz sections
if st.session_state["flashcards"]:
    flashcard_review_editor()
    render_export_section()

quiz_mode()
