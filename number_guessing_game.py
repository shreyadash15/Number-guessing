"""
Number Guessing Game (Text-Based)
---------------------------------
- The computer picks a number between 1 and 100.
- You guess until you get it right (or you run out of attempts on some difficulties).
- Hints after each guess: "Too High" / "Too Low".
- Tracks high scores (fewest attempts) per difficulty in a local JSON file.

Author: (Your Name)
"""

from __future__ import annotations

import json
import os
import random
from typing import Dict, Optional, Tuple

HIGHSCORE_FILE = "guess_highscore.json"

DIFFICULTIES = {
    "E": {"name": "Easy", "max_attempts": None},  
    "N": {"name": "Normal", "max_attempts": 10},
    "H": {"name": "Hard", "max_attempts": 7},
}


def clear_screen() -> None:
    """Attempt to clear the terminal screen (purely cosmetic)."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner() -> None:
    """Print a friendly banner."""
    print("=" * 52)
    print("          NUMBER GUESSING GAME (1 - 100)  ")
    print("=" * 52)


def print_instructions() -> None:
    """Display game instructions."""
    print_banner()
    print("How to Play:")
    print("  • The computer thinks of a number between 1 and 100.")
    print("  • You guess the number. After each guess you'll see:")
    print('      - "Too High" if your guess is bigger than the secret')
    print('      - "Too Low"  if your guess is smaller than the secret')
    print("  • Keep guessing until you find the correct number!")
    print("  • On Normal/Hard you have a limited number of attempts.")
    print("  • Your best (fewest attempts) per difficulty is saved.\n")
    print("Controls:")
    print("  • Enter integers only (1–100).")
    print("  • Use the menu to Play, see High Scores, or Exit.\n")


def input_choice(prompt: str, valid: Tuple[str, ...]) -> str:
    """
    Prompt for a single-letter choice until valid.
    Returns the uppercase chosen letter.
    """
    while True:
        try:
            choice = input(prompt).strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting... Bye!")
            raise SystemExit(0)
        if choice in valid:
            return choice
        print(f"Invalid choice. Pick one of: {', '.join(valid)}")


def input_int(prompt: str, min_value: int, max_value: int) -> int:
    """
    Prompt for an integer between min_value and max_value (inclusive).
    Re-prompts on invalid input or out-of-range values.
    """
    while True:
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting... Bye!")
            raise SystemExit(0)
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a valid integer.")
            continue
        if not (min_value <= value <= max_value):
            print(f"Value must be between {min_value} and {max_value}.")
            continue
        return value


def load_highscores() -> Dict[str, Optional[int]]:
    """
    Load highscores from JSON file.
    Returns dict mapping difficulty name -> fewest attempts (or None).
    """
    # Initialize default highscores
    scores: Dict[str, Optional[int]] = {d["name"]: None for d in DIFFICULTIES.values()}
    if not os.path.exists(HIGHSCORE_FILE):
        return scores
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
       
        for diff_name in scores.keys():
            if isinstance(data.get(diff_name), int):
                scores[diff_name] = data[diff_name]
    except (json.JSONDecodeError, OSError):
        
        pass
    return scores


def save_highscores(scores: Dict[str, Optional[int]]) -> None:
    """Save highscores to JSON file (best-effort)."""
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except OSError:
        
        pass


def update_highscore(
    scores: Dict[str, Optional[int]], difficulty_name: str, attempts: int
) -> bool:
    """
    Update the highscore table if `attempts` is better (fewer) than existing.
    Returns True if a new record was set.
    """
    best = scores.get(difficulty_name)
    if best is None or attempts < best:
        scores[difficulty_name] = attempts
        save_highscores(scores)
        return True
    return False


def choose_difficulty() -> Tuple[str, int | None, str]:
    """
    Ask the user to pick a difficulty.
    Returns (difficulty_key, max_attempts, difficulty_name).
    """
    print("\nChoose Difficulty:")
    for key, meta in DIFFICULTIES.items():
        lim = "∞" if meta["max_attempts"] is None else str(meta["max_attempts"])
        print(f"  {key}) {meta['name']:6s}  — Max Attempts: {lim}")
    diff_key = input_choice("Your choice (E/N/H): ", tuple(DIFFICULTIES.keys()))
    diff_name = DIFFICULTIES[diff_key]["name"]
    max_attempts = DIFFICULTIES[diff_key]["max_attempts"]
    return diff_key, max_attempts, diff_name


def play_round(max_attempts: Optional[int]) -> int:
    """
    Run a single round of the game. Returns the number of attempts taken.
    Raises SystemExit on Ctrl+C/Z to exit cleanly.
    """
    secret = random.randint(1, 100)
    attempts = 0

    while True:
     
        if max_attempts is not None:
            remaining = max_attempts - attempts
            if remaining <= 0:
                print("\n Out of attempts! Better luck next time.")
                print(f"The secret number was: {secret}\n")
                # Return a sentinel high attempts so it won't set a record
                return 10**9
            print(f"\nAttempts remaining: {remaining}")

        guess = input_int("Enter your guess (1-100): ", 1, 100)
        attempts += 1

        if guess == secret:
            print(f" Correct! You got it in {attempts} attempt(s). \n")
            return attempts
        elif guess < secret:
            print("Too Low.")
        else:
            print("Too High.")

       
        diff = abs(secret - guess)
        if diff <= 5:
            print(" Very close!")
        elif diff <= 10:
            print(" Getting warm.")
        else:
            print("  Cold.")


def show_highscores(scores: Dict[str, Optional[int]]) -> None:
    """Pretty-print the highscores table."""
    print_banner()
    print("High Scores (fewest attempts):\n")
    for name in [d["name"] for d in DIFFICULTIES.values()]:
        best = scores.get(name)
        print(f"  {name:6s} : {'—' if best is None else best}")
    print()  # newline


def reset_highscores() -> None:
    """Reset (delete) local highscores file after confirmation."""
    print("\nThis will erase all saved highscores.")
    confirm = input_choice("Are you sure? (Y/N): ", ("Y", "N"))
    if confirm == "Y":
        try:
            if os.path.exists(HIGHSCORE_FILE):
                os.remove(HIGHSCORE_FILE)
            print("Highscores reset.\n")
        except OSError:
            print("Could not delete highscore file (permission issue).")
    else:
        print("Canceled.\n")


def menu_loop() -> None:
    """Main menu loop. Runs until the user chooses to exit."""
    scores = load_highscores()

    while True:
        clear_screen()
        print_banner()
        print("Menu:")
        print("  1) Play")
        print("  2) Instructions")
        print("  3) High Scores")
        print("  4) Reset High Scores")
        print("  5) Exit\n")

        choice = input_choice("Select an option (1-5): ", ("1", "2", "3", "4", "5"))

        if choice == "1":
            clear_screen()
            print_banner()
            diff_key, max_attempts, diff_name = choose_difficulty()
            print(f"\nDifficulty selected: {diff_name}\n")
            attempts = play_round(max_attempts)
            if attempts < 10**9:
                if update_highscore(scores, diff_name, attempts):
                    print(f" New {diff_name} record: {attempts} attempt(s)!")
                else:
                    best = scores.get(diff_name)
                    best_str = "—" if best is None else str(best)
                    print(f"Best {diff_name} so far: {best_str} attempt(s).")
            input("Press Enter to return to menu...")

        elif choice == "2":
            clear_screen()
            print_instructions()
            input("Press Enter to return to menu...")

        elif choice == "3":
            clear_screen()
            show_highscores(scores)
            input("Press Enter to return to menu...")

        elif choice == "4":
            reset_highscores()
            scores = load_highscores()  
        elif choice == "5":
            print("\nThanks for playing. Goodbye! ")
            break


def main() -> None:
    """Program entry point."""
    try:
        menu_loop()
    except SystemExit:
        
        pass


if __name__ == "__main__":
    main()
