"""Command-line demo of the HR Policy Assistant.

Run with:  python main.py
"""

from hr_assistant.logger import get_logger
from hr_assistant.pipeline import ask, build_hr_assistant

logger = get_logger(__name__)


def main():
    logger.info("=== CLI run started ===")
    assistant = build_hr_assistant()
    logger.info("Assistant ready")

    demo_questions = [
        "How many casual leaves can an employee take?",
        "What is the hotel allowance for domestic travel?",
        "How many work from home days are allowed per month?",
    ]

    for question in demo_questions:
        logger.info("QUESTION: %s", question)
        answer = ask(assistant, question)
        logger.info("ANSWER: %s", answer)

    logger.info("=== CLI run finished ===")


if __name__ == "__main__":
    main()
