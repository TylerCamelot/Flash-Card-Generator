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

## AI Prompt Log (Copy/Paste Prompts Used)

Below are the prompts I used with ChatGPT during development. These prompts guided the majority of the application’s architecture, logic, UI, and refactoring.

---

### Prompt 1 — Streamlit App Scaffold
I am building a Streamlit application called “Study Flashcard Generator.”  
Please generate the initial app.py structure with:
- Page title and description
- Text area for pasting study material
- Sidebar configuration (number of cards, difficulty)
- A “Generate Flashcards” button  
Use clean, well-commented Python code.

---

### Prompt 2 — LLM Flashcard Generation (Strict JSON)
Write a Python function that takes study material text and uses an LLM  
to generate flashcards in STRICT JSON format only.

Each flashcard should include:
- question
- answer
- difficulty (Easy / Medium / Hard)

Include robust error handling and retry once if JSON parsing fails.

---

### Prompt 3 — Mock Mode Fallback (No LLM)
Add a fallback “Mock Mode” for flashcard generation that does not use an LLM.

The mock generator should:
- Extract term–definition pairs when possible
- Create reasonable question–answer flashcards
- Avoid echoing the input text
- Still support quiz functionality and scoring

Provide Python code suitable for a Streamlit app.

---

### Prompt 4 — Flashcard Review UI (Editable)
Using Streamlit, display generated flashcards in an editable review section.

Users should be able to:
- Edit questions and answers
- Delete selected flashcards
- Persist changes using st.session_state

Include clean UI and inline comments.

---

### Prompt 5 — Quiz Mode with Scoring
Add a quiz mode to the Streamlit app where:
- Flashcards are shown one at a time in random order
- Users can reveal the answer
- Users self-grade as correct or incorrect
- The app tracks score and displays missed questions at the end

Use session state to manage quiz progress.

---

### Prompt 6 — Refactor for Readability + Robustness
Refactor the Streamlit app to improve readability and robustness.

Add:
- Clear docstrings
- Inline comments
- Error handling for empty input, API failures, and invalid user actions

Ensure the app remains fully functional without an API key.

---

### Prompt 7 — Single Executable File
Combine all of this code into a single code file that is ready to execute.


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

---
## 8. Screenshots
<img width="540" height="931" alt="image" src="https://github.com/user-attachments/assets/96832b6f-590d-420b-99ac-985c8668f1ad" />
<img width="600" height="892" alt="image" src="https://github.com/user-attachments/assets/d3073ac0-1689-4b34-81ba-67420604dad5" />
<img width="756" height="882" alt="image" src="https://github.com/user-attachments/assets/d42d64b8-64c9-4266-959e-498d1e7debe5" />
<img width="547" height="936" alt="image" src="https://github.com/user-attachments/assets/3535e0e7-6a4b-4e6e-bbd7-26fadfe6ae70" />
<img width="662" height="918" alt="image" src="https://github.com/user-attachments/assets/aa9b3e44-e92d-45de-a2b5-98e1f55f35ce" />
<img width="628" height="880" alt="image" src="https://github.com/user-attachments/assets/da4e2ea3-e745-4c88-8aa5-6d28ff8e2bb3" />
<img width="502" height="930" alt="image" src="https://github.com/user-attachments/assets/3c0823fb-9402-46d1-ad74-4ef905ae35d9" />








