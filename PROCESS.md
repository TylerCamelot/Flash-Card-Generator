# PROCESS.md  
**Study Flashcard Generator (Streamlit + LLM)**

---

## 1. AI Assistant(s) Used

I primarily used **ChatGPT** as my AI coding assistant throughout the development of this project.

ChatGPT was used to:
- Design the overall application workflow
- Generate the initial Streamlit UI structure
- Implement flashcard generation logic
- Add quiz functionality and session state management
- Design fallback logic when no LLM API key is available
- Refactor and document the final codebase

No code was copied from external repositories; all functionality was developed through iterative prompting and refinement with the AI assistant.

---

## 2. Key Prompts Used (5–10 Examples)

Below are representative prompts used during development (copied verbatim or lightly shortened for clarity):

1. **“Generate the initial `app.py` structure using Streamlit that includes a title, a text area for pasting study material, a sidebar for configuration, and a ‘Generate Flashcards’ button.”**

2. **“Write a Python function that takes study material text and uses an LLM to generate flashcards in JSON format, with question, answer, and difficulty fields, including error handling.”**

3. **“Improve the flashcard generation function so the LLM is forced to return valid JSON only, retry once if parsing fails, and raise a user-friendly error if it fails again.”**

4. **“Using Streamlit, display generated flashcards in an editable format where users can review, edit, delete cards, and store results in `st.session_state`.”**

5. **“Add a quiz mode where flashcards are shown one at a time in random order, allow self-grading, track score, and display missed questions.”**

6. **“Add a fallback ‘Mock Mode’ that generates reasonable flashcards without an LLM so the app remains fully functional without an API key.”**

7. **“Improve Mock Mode so it extracts term-definition pairs, formulas, and mnemonics instead of echoing text.”**

8. **“Add functionality to export flashcards to Anki (TSV) and Quizlet (CSV) with download buttons in Streamlit.”**

9. **“Refactor the Streamlit app for readability, add docstrings, inline comments, and robust error handling.”**

---

## 3. Challenges Encountered and Solutions

### Challenge 1: LLM API Quota and Cost Constraints
**Problem:**  
While integrating the OpenAI API, quota and billing limits prevented reliable use of the LLM for every generation.

**Solution:**  
A **Mock Mode** fallback was implemented using heuristic-based NLP techniques (regex parsing, sentence chunking, mnemonic detection). This ensured the app remained fully functional without an API key.

---

### Challenge 2: Low-Quality or “Echo” Flashcards
**Problem:**  
Early generations sometimes produced flashcards where answers repeated the question or were unrelated.

**Solution:**  
A **quality-filtering layer** was added to:
- Detect echo answers
- Flag very short or low-information responses
- Repair cards heuristically or via optional LLM-based repair

---

### Challenge 3: Session State and Data Contamination
**Problem:**  
Switching study topics could cause old flashcards to leak into new generations.

**Solution:**  
Flashcards and quiz state are reset whenever new study material is submitted or cards are regenerated, preventing cross-topic contamination.

---

### Challenge 4: Quiz Flow and User Experience
**Problem:**  
Managing quiz progression, answer reveal logic, and scoring required careful state management.

**Solution:**  
Structured quiz state variables (`quiz_pos`, `quiz_order`, `quiz_correct`, etc.) were implemented using `st.session_state`, along with guardrails for invalid user actions.

---

## 4. What Worked Well vs. What Didn’t

### What Worked Well
- Rapid UI development with Streamlit
- JSON-enforced LLM responses for structured output
- Mock Mode heuristics for cost-free reliability
- Self-grading quiz design (simple and robust)
- Export to Anki and Quizlet for real-world usability

### What Didn’t Work as Expected
- Pure heuristic generation without filtering produced weak cards
- Relying solely on LLM output without validation caused failures
- Difficulty labels alone do not fully control semantic difficulty

These issues were resolved through validation, filtering, and fallback design.

---

## 5. AI-Generated vs. Manually Written Code

Estimated breakdown:
- **AI-generated code:** ~85–90%
- **Manually written/edited code:** ~10–15%

Manual work focused on wiring components together, testing edge cases, and light refactoring.

This exceeds the requirement that at least 80% of the code be AI-generated.

---

## 6. Time Saved Estimate

Estimated effort without AI assistance: **12–15 hours**  
Actual development time with AI assistance: **4–5 hours**

**Estimated time saved:** **7–10 hours**

---

## 7. Final Reflection

This project demonstrated how AI can be used not only to generate code, but to iteratively design, debug, and improve an application.

Key takeaways include:
- Effective prompt engineering
- Validating and repairing AI output
- Designing fallback systems for reliability
- Balancing cost, robustness, and usability

The final application is fully functional, resilient to API failures, and suitable for real-world use as a study aid.

