# 📚 Study Flashcard Generator

A Streamlit-based application that automatically generates study flashcards from pasted text using a Large Language Model (LLM), with a robust fallback **Mock Mode** to ensure full functionality without an API key. Users can review and edit flashcards, quiz themselves with scoring, and export cards to **Anki** or **Quizlet** formats.

---

## 🚀 Features

- **Flashcard Generation**
  - Generate flashcards from raw study material using an LLM
  - Control number of cards and difficulty level (Easy / Medium / Hard)
  - Automatic fallback to Mock Mode if no API key is available

- **Flashcard Review & Editing**
  - Edit questions and answers inline
  - Change difficulty levels
  - Delete individual cards or clear all cards
  - All changes persist using Streamlit session state

- **Quiz Mode**
  - Randomized, one-question-at-a-time quiz
  - Reveal answers and self-grade (correct / incorrect)
  - Tracks score and displays final results
  - Review missed questions with correct answers

- **Export Options**
  - Export to **Anki** (TSV: Front / Back / Tags)
  - Export to **Quizlet** (CSV: Term / Definition)
  - Export reflects any edits made to flashcards

- **Robust Error Handling**
  - Handles empty input
  - Gracefully manages API failures
  - Prevents invalid quiz actions
  - Ensures app remains functional in all modes

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** (UI framework)
- **OpenAI API** (optional, for LLM-based generation)
- **CSV / TSV** for flashcard export

---

## 📂 Project Structure


