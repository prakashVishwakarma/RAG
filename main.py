"""Command-line demo of the HR Policy Assistant.

Run with:  python main.py
"""

from hr_assistant.pipeline import ask, build_hr_assistant


def main():
    print("Building the HR policy assistant...")
    assistant = build_hr_assistant()
    print("Assistant ready!\n")

    demo_questions = [
        "How many casual leaves can an employee take?",
        "What is the hotel allowance for domestic travel?",
        "How many work from home days are allowed per month?",
    ]

    for question in demo_questions:
        print("=" * 60)
        print("QUESTION:", question)
        print("-" * 60)
        answer = ask(assistant, question)
        print("ANSWER:", answer)
        print("=" * 60)
        print()


if __name__ == "__main__":
    main()
