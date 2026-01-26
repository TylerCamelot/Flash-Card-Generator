# 📚 Study Flashcard Generator

A Streamlit-based application that automatically generates study flashcards from pasted text using a Large Language Model (LLM), with a robust fallback **Mock Mode** to ensure full functionality without an API key. Users can review and edit flashcards, quiz themselves with scoring, and export cards to **Anki** or **Quizlet** formats.

---
## How to use
- Step 1: download app.py and docgen.py
- Step 2: type streamlit run app.py into console (run locally)
- Step 3: use the Usage list below to use the website

---
## Video Demo
- https://www.youtube.com/watch?v=isUMJF7xWZg
---
## Usage
  - Generate Flashcards: copy notes/information into text box and click generate flashcards
  - Editing Flashcards: edit flashcards and answers inline if necessary
  - Difficulty/Flashcard Number Adjustemnt: use tab on the left hand side to adjust the difficulty and amount of flashcards generated
  - Mode Change: can change modes from LLM mode to mock mode (default if none is available)
  - Quiz Mode: Once flashcards are generated you can activate a quiz mode at the bottom
  - Download Flashcards: Flashcards can be download to Anki or Quizlet
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

## Value
- The value behind this project is clear, it provides students with an easy-to-use tool to automatically create flashcards from their notes with little effort.

---

## Images
<img width="540" height="931" alt="image" src="https://github.com/user-attachments/assets/ca0d3fcd-50aa-4b36-b4a8-075c017f4e60" />
<img width="600" height="892" alt="image" src="https://github.com/user-attachments/assets/eb9ad550-3818-4a3c-a61a-84d3b5bb7131" />
<img width="756" height="882" alt="image" src="https://github.com/user-attachments/assets/460ec541-03fe-4d92-a17b-cba0e409d005" />
<img width="547" height="936" alt="image" src="https://github.com/user-attachments/assets/eb9b51bf-5c9f-47d9-bed6-43c9bb7b91cc" />
<img width="662" height="918" alt="image" src="https://github.com/user-attachments/assets/e05fdf6b-89b3-4687-b794-9cd8ee312218" />
<img width="628" height="880" alt="image" src="https://github.com/user-attachments/assets/83353489-aecf-4cbb-816c-6972114e33dd" />
<img width="502" height="930" alt="image" src="https://github.com/user-attachments/assets/32bc6725-5957-4eca-930c-02feb11d885c" />









