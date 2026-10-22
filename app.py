from rag import ask_question

print("Company Policy Assistant (type 'exit' to quit)")

while True:
    question = input("\nYour question: ").strip()

    if question.lower() in ("exit", "quit"):
        break

    if question == "":
        continue

    answer = ask_question(question)
    print(f"\nAnswer: {answer}")
