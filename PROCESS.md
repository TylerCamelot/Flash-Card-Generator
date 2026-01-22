# PROCESS.md — Study Flashcard Generator

## 1. AI Assistant(s) Used
- **ChatGPT** (primary AI assistant)

ChatGPT was used throughout the project for:
- Application architecture and planning
- Streamlit UI generation
- LLM prompt engineering
- Session state management
- Quiz logic and scoring
- Error handling patterns
- Mock Mode fallback design
- Export functionality (CSV / TSV)
- Code refactoring and documentation

No external codebases or templates were copied; all logic was produced through iterative prompting and refinement.

---

## 2. Key Prompts Used (5–10)

Below are representative prompts used during development (copied verbatim or lightly trimmed for clarity):

1. **Initial App Structure**
   > I am working in PyCharm and want to build a Streamlit application called “Study Flashcard Generator.” Please generate the initial `app.py` structure using Streamlit that includes a title, a text area for pasting study material, a sidebar for configuration, and a “Generate Flashcards” button.

2. **LLM Flashcard Generation**
   > Write a Python function that takes study material text and uses an LLM to generate flashcards in JSON format. Each flashcard should include `question`, `answer`, and `difficulty`.

3. **JSON Reliability**
   > Improve the flashcard generation function so the LLM is forced to return valid JSON only. Add logic that retries once if JSON parsing fails and raises a user-friendly error if it fails again.

4. **Flashcard Review UI**
   > Using Streamlit, display the generated flashcards in an editable format where users can review the question and answer, delete cards they don’t like, and store the results in `st.session_state`.

5. **Quiz Mode**
   > Add a quiz mode to the Streamlit app where flashcards are presented one at a time in random order. Allow the user to answer each question, self-grade as correct or incorrect, and track the quiz score.

6. **Mock Mode Fallback**
   > Add a fallback “Mock Mode” that generates simple flashcards from the input text if no LLM API key is available so the app remains fully functional.

7. **Export Functionality**
   > Add functionality to export the final set of flashcards to a CSV file compatible with Anki or Quizlet and provide a download button in Streamlit.

8. **Refactoring & Documentation**
   > Refactor the Streamlit app code to improve readability, add docstrings and inline comments, and ensure error handling is present for empty input, API failures, and invalid user actions.

---

## 3. Challenges and Solutions

### Challenge 1: Unreliable LLM Output Formatting
**Problem:** LLM responses occasionally included extra text or invalid JSON, breaking parsing.  
**Solution:** Enforced strict JSON-only output in the prompt and added retry logic with clear error messages if parsing failed.

---

### Challenge 2: Streamlit Re-run Behavior
**Problem:** Streamlit re-runs the script on every interaction, causing state to reset unexpectedly.  
**Solution:** Centralized all mutable data (flashcards, quiz state, scores) in `st.session_state` and added defensive checks when flashcards changed mid-quiz.

---

### Challenge 3: API Dependency for Demos
**Problem:** The app could fail during demos if an API key was missing or the API was unavailable.  
**Solution:** Implemented a fully functional **Mock Mode** fallback that generates flashcards without an LLM.

---

## 4. What Worked vs. What Didn’t

### What Worked Well
- Using AI to scaffold Streamlit UI dramatically reduced setup time
- Iterative prompting improved code quality over time
- Mock Mode ensured the app was always usable
- Self-grading quiz logic simplified scoring and improved reliability

### What Didn’t Work / Lessons Learned
- Early versions without strict JSON enforcement caused runtime errors
- Attempting automatic quiz grading via LLM added unnecessary complexity and was removed
- Mixing UI logic and business logic early on reduced readability (fixed during refactor)

---

## 5. AI-Generated vs. Manually Written Code

- **AI-generated code:** ~85–90%
- **Manually written code:** ~10–15%

Manual work primarily involved:
- Minor logic tweaks
- File organization
- Testing edge cases
- Adjusting UI wording and layout

---

## 6. Time Saved Estimate

Estimated **8–12 hours saved** compared to building the application entirely from scratch without AI assistance.

Time savings were especially significant in:
- UI scaffolding
- Session state patterns
- Error handling design
- Export logic
- Refactoring and documentation
