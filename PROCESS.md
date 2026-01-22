## AI Assistant Used
ChatGPT


## Prompts
### Prompt 1 — Project Scaffolding
I am working in PyCharm and want to build a Streamlit application called “Study Flashcard Generator.”  
Please generate the initial `app.py` structure using Streamlit that includes a title, a text area for pasting study material, a sidebar for configuration, and a “Generate Flashcards” button.

---

### Prompt 2 — LLM-Based Flashcard Generation
Write a Python function that takes study material text and uses an LLM to generate flashcards in JSON format.  
Each flashcard should include `question`, `answer`, and `difficulty`.  
The function should include error handling for invalid or empty LLM responses.

---

### Prompt 3 — Strict JSON Enforcement & Retry Logic
Improve the flashcard generation function so the LLM is forced to return valid JSON only.  
Add logic that retries once if JSON parsing fails, and raises a user-friendly error if it fails again.

---

### Prompt 4 — Streamlit Flashcard Review UI
Using Streamlit, display the generated flashcards in an editable format where users can review the question and answer, delete cards they don’t like, and store the results in `st.session_state`.

---

### Prompt 5 — Quiz Mode with Scoring
Add a quiz mode to the Streamlit app where flashcards are presented one at a time in random order.  
Allow the user to answer each question, self-grade as correct or incorrect, and track the quiz score.  
Display the final score and list incorrectly answered questions.

---

### Prompt 6 — Difficulty & Card Count Controls
Extend the Streamlit sidebar to allow the user to choose the number of flashcards (slider) and difficulty level (Easy / Medium / Hard), and ensure these parameters are passed to the LLM generation function.

---

### Prompt 7 — Mock Fallback Mode
Add a fallback “Mock Mode” that generates simple flashcards from the input text if no LLM API key is available.  
This mode should still allow quiz functionality and scoring so the app remains fully functional.

---

### Prompt 8 — Flashcard Export
Add functionality to export the final set of flashcards to a CSV file compatible with Anki or Quizlet, and provide a download button in Streamlit.

---

### Prompt 9 — Code Quality & Error Handling
Refactor the Streamlit app code to improve readability, add docstrings and inline comments, and ensure error handling is present for empty input, API failures, and invalid user actions.

---

### Prompt 10 — Project Documentation
Generate a professional README.md and PROCESS.md for this project.  
PROCESS.md should include: AI tools used, key prompts, challenges and solutions, estimated AI-generated percentage, and time saved estimate.

## Challenges and Solutions


## What Worked and What Didn't

## AI Generated % vs. Written Manually
AI Generated: 100% 
Written Manually: 0%

## Time Saved Estimate
Weeks
