# Quiz Application (Tkinter)

A desktop quiz application built with Python and Tkinter that loads multiple-choice questions from CSV or JSON, guides users through the quiz with validation, and stores results to CSV or JSON for later review.

## About
Quiz Application is a lightweight, GUI-based quiz tool intended for quick knowledge checks and demos. It supports:
- Multiple-choice questions sourced from CSV or JSON files.
- Inline feedback on each question.
- Automatic scoring with percentage calculation.
- Persistent result storage to CSV or JSON for simple reporting or reuse.

## Features
- **Dual question formats:** Load questions from `questions.csv` or `questions.json`.
- **Input validation:** Ensures required headers/fields exist; warns if options are missing.
- **Progress + feedback:** Shows current question index and immediate correctness feedback.
- **Result export:** Saves date, score, total, and percentage to CSV or JSON.
- **Responsive layout:** Centers the window and wraps question text for readability.

## Tech Stack
- **Language:** Python 3.x
- **GUI:** Tkinter
- **Data formats:** CSV, JSON
- **Persistence:** Local filesystem (CSV/JSON)

## Requirements
- Python 3.8+ (Tkinter is bundled with most Python distributions)
- Dependencies: Standard library only (csv, json, os, datetime, tkinter)

## Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/hanumanthuNani/QuizApplication.git
   cd QuizApplication
   ```
2. Ensure you have a questions file (`questions.csv` or `questions.json`) in the project root.

3. Run the app:
   ```bash
   python quiz_app.py --questions questions.csv --results results.csv
   ```
   - `--questions` (optional): Path to a CSV or JSON question file. Defaults to `questions.csv` if present, else `questions.json`.
   - `--results` (optional): Path to save results (CSV or JSON). Defaults to `results.csv`.

## Question File Formats

### CSV (`questions.csv`)
Required headers: `question, option1, option2, option3, option4, correct_answer`
```csv
question,option1,option2,option3,option4,correct_answer
What is the capital of France?,Paris,Lyon,Marseille,Toulouse,Paris
```

### JSON (`questions.json`)
Each item must include `question`, an `options` array of four choices, and `correct_answer`.
```json
[
  {
    "question": "What is the capital of France?",
    "options": ["Paris", "Lyon", "Marseille", "Toulouse"],
    "correct_answer": "Paris"
  }
]
```

## Results Storage
- CSV: Appends rows with `date, score, total, percentage`.
- JSON: Appends entries to an array of result objects.
- Default output file is `results.csv` unless overridden via `--results`.

## Project Structure
- `quiz_app.py` — Main Tkinter application, quiz engine, data loading, and result storage.
- `questions.csv` — Sample CSV questions.
- `questions.json` — Sample JSON questions.
- `quiz_app.png` — Screenshot of the application UI.

## Running the GUI
- The window centers itself at 720×440 by default.
- Users must select an answer before moving to the next question or submitting.
- On completion, a results screen shows totals and percentages, and the results file is updated.

## Author
- **hanumanthuNani** — [GitHub Profile](https://github.com/hanumanthuNani)

## License
This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.
