"""Tkinter Quiz application supporting CSV/JSON questions and result storage."""

import csv
import datetime
import json
import os
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional


class Question:
    def __init__(self, question: str, options: List[str], correct_answer: str):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer


class QuizDataLoader:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> List[Question]:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Question file not found: {self.filepath}")

        extension = os.path.splitext(self.filepath)[1].lower()
        if extension == ".csv":
            return self._load_csv()
        if extension == ".json":
            return self._load_json()

        raise ValueError("Unsupported question file. Use CSV or JSON.")

    def _load_csv(self) -> List[Question]:
        questions: List[Question] = []
        with open(self.filepath, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            required_fields = {"question", "option1", "option2", "option3", "option4", "correct_answer"}
            if not required_fields.issubset(reader.fieldnames or []):
                raise ValueError("CSV must include question, option1..4, correct_answer headers.")
            for row in reader:
                options = [row["option1"], row["option2"], row["option3"], row["option4"]]
                questions.append(Question(row["question"], options, row["correct_answer"]))
        return questions

    def _load_json(self) -> List[Question]:
        questions: List[Question] = []
        with open(self.filepath, encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)
        for item in data:
            options = item.get("options") or []
            if len(options) < 4:
                raise ValueError("Each question needs four options.")
            questions.append(Question(item.get("question", ""), options[:4], item.get("correct_answer", "")))
        return questions


class ResultsStorage:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def save(self, score: int, total: int) -> None:
        percentage = round((score / total) * 100, 2) if total else 0
        entry = {
            "date": datetime.datetime.now().isoformat(timespec="seconds"),
            "score": score,
            "total": total,
            "percentage": percentage,
        }
        extension = os.path.splitext(self.filepath)[1].lower()
        if extension == ".csv":
            self._append_csv(entry)
        else:
            self._append_json(entry)

    def _append_csv(self, entry: dict) -> None:
        file_exists = os.path.exists(self.filepath)
        with open(self.filepath, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["date", "score", "total", "percentage"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(entry)

    def _append_json(self, entry: dict) -> None:
        data = []
        if os.path.exists(self.filepath):
            with open(self.filepath, encoding="utf-8") as jsonfile:
                try:
                    data = json.load(jsonfile)
                except json.JSONDecodeError:
                    data = []
        if not isinstance(data, list):
            data = []
        data.append(entry)
        with open(self.filepath, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, indent=2)


class QuizEngine:
    def __init__(self, questions: List[Question]):
        self.questions = questions
        self.current_index = 0
        self.answers: List[Optional[str]] = [None] * len(questions)

    def current_question(self) -> Question:
        return self.questions[self.current_index]

    def record_answer(self, answer: str) -> None:
        self.answers[self.current_index] = answer

    def next_question(self) -> None:
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1

    def is_last(self) -> bool:
        return self.current_index == len(self.questions) - 1

    def score(self) -> int:
        score = 0
        for question, user_answer in zip(self.questions, self.answers):
            if user_answer == question.correct_answer:
                score += 1
        return score

    def correct_count(self) -> int:
        return self.score()

    def wrong_count(self) -> int:
        return len(self.questions) - self.correct_count()


class QuizApp:
    def __init__(self, root: tk.Tk, questions: List[Question], results_path: str):
        self.root = root
        self.engine = QuizEngine(questions)
        self.results_storage = ResultsStorage(results_path)
        self.selected_option = tk.StringVar()

        self.root.title("Python Quiz Application")
        self.center_window(720, 440)

        self.container = tk.Frame(self.root, padx=20, pady=20)
        self.container.pack(fill="both", expand=True)

        self._build_quiz_ui()
        self.show_question()

    def center_window(self, width: int, height: int) -> None:
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coord = int((screen_width / 2) - (width / 2))
        y_coord = int((screen_height / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x_coord}+{y_coord}")

    def _build_quiz_ui(self) -> None:
        title = tk.Label(self.container, text="Python Quiz Application", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.progress_label = tk.Label(self.container, text="", font=("Arial", 12))
        self.progress_label.grid(row=1, column=0, sticky="w", pady=5)

        self.question_label = tk.Label(self.container, text="", font=("Arial", 14), wraplength=640, justify="left")
        self.question_label.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")

        self.option_buttons: List[tk.Radiobutton] = []
        for i in range(4):
            btn = tk.Radiobutton(
                self.container,
                text="",
                variable=self.selected_option,
                value="",
                font=("Arial", 12),
                anchor="w",
                justify="left",
            )
            btn.grid(row=3 + i, column=0, columnspan=2, sticky="w", pady=2)
            self.option_buttons.append(btn)

        self.feedback_label = tk.Label(self.container, text="", font=("Arial", 12))
        self.feedback_label.grid(row=7, column=0, columnspan=2, pady=(10, 5), sticky="w")

        self.next_button = tk.Button(self.container, text="Next", command=self.on_next, width=12)
        self.next_button.grid(row=8, column=0, pady=10, sticky="w")

        self.submit_button = tk.Button(self.container, text="Submit", command=self.on_submit, width=12)
        self.submit_button.grid(row=8, column=1, pady=10, sticky="e")

    def show_question(self) -> None:
        question = self.engine.current_question()
        self.selected_option.set("")

        self.progress_label.config(
            text=f"Question {self.engine.current_index + 1} / {len(self.engine.questions)}"
        )
        self.question_label.config(text=question.question)

        for btn, option in zip(self.option_buttons, question.options):
            btn.config(text=option, value=option, state="normal")

        if self.engine.current_index == 0 and not any(self.engine.answers):
            self.feedback_label.config(text="")
        self._update_navigation_buttons()

    def on_next(self) -> None:
        # Prevent moving forward without a selection to avoid skipping questions.
        if not self.selected_option.get():
            messagebox.showwarning("Select an option", "Please select an option before moving on.")
            return

        question = self.engine.current_question()
        chosen = self.selected_option.get()
        # Store the answer before moving to the next question.
        self.engine.record_answer(chosen)

        feedback_text = (
            "Correct! 🎉" if chosen == question.correct_answer else f"Wrong! Correct answer: {question.correct_answer}"
        )
        self.feedback_label.config(text=feedback_text)

        if not self.engine.is_last():
            self.engine.next_question()
            self.show_question()
        else:
            self.on_submit()

    def on_submit(self) -> None:
        if not self.selected_option.get():
            messagebox.showwarning("Select an option", "Please select an option before submitting.")
            return

        question = self.engine.current_question()
        chosen = self.selected_option.get()
        self.engine.record_answer(chosen)

        feedback_text = (
            "Correct! 🎉" if chosen == question.correct_answer else f"Wrong! Correct answer: {question.correct_answer}"
        )
        self.feedback_label.config(text=feedback_text)

        self.show_results()

    def show_results(self) -> None:
        score = self.engine.score()
        total = len(self.engine.questions)
        correct = self.engine.correct_count()
        wrong = self.engine.wrong_count()
        percentage = round((score / total) * 100, 2) if total else 0

        try:
            self.results_storage.save(score, total)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Save Error", f"Could not save results: {exc}")

        self.container.destroy()
        result_frame = tk.Frame(self.root, padx=20, pady=20)
        result_frame.pack(fill="both", expand=True)

        tk.Label(result_frame, text="Quiz Completed!", font=("Arial", 18, "bold")).pack(pady=(0, 10))
        tk.Label(result_frame, text=f"Total Score: {score} / {total}", font=("Arial", 14)).pack(anchor="w")
        tk.Label(result_frame, text=f"Correct Answers: {correct}", font=("Arial", 14)).pack(anchor="w")
        tk.Label(result_frame, text=f"Wrong Answers: {wrong}", font=("Arial", 14)).pack(anchor="w")
        tk.Label(result_frame, text=f"Percentage: {percentage}%", font=("Arial", 14)).pack(anchor="w", pady=(0, 10))

        tk.Button(result_frame, text="Close", command=self.root.destroy, width=12).pack(pady=10)

    def _update_navigation_buttons(self) -> None:
        if self.engine.is_last():
            self.next_button.grid_remove()
            self.submit_button.grid()
        else:
            self.next_button.grid()
            self.submit_button.grid_remove()


def resolve_question_file(preferred: Optional[str] = None) -> str:
    if preferred and os.path.exists(preferred):
        return preferred
    if os.path.exists("questions.csv"):
        return "questions.csv"
    if os.path.exists("questions.json"):
        return "questions.json"
    raise FileNotFoundError("No question file found. Please provide questions.csv or questions.json.")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Python Quiz Application (Tkinter)")
    parser.add_argument("--questions", help="Path to question file (CSV or JSON).", default=None)
    parser.add_argument("--results", help="Path to results file (CSV or JSON).", default="results.csv")
    args = parser.parse_args()

    try:
        question_file = resolve_question_file(args.questions)
        questions = QuizDataLoader(question_file).load()
    except Exception as exc:  # noqa: BLE001
        messagebox.showerror("Load Error", f"Could not load questions: {exc}")
        return

    root = tk.Tk()
    QuizApp(root, questions, args.results)
    root.mainloop()


if __name__ == "__main__":
    main()
