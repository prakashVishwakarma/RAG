"""Step 1: read and clean policy PDFs from the data folder."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from hr_assistant import config


def is_continuation(previous_line, line):
    """Return True if `line` is the rest of a sentence the PDF wrapped onto a new line."""
    if line.startswith("•"):
        return False  # a new bullet point always starts a new line

    if line[0].islower():
        return True  # e.g. "possible." after "...whenever reasonably"

    # A long line that doesn't end a sentence was wrapped by the PDF
    return len(previous_line) >= 60 and not previous_line.endswith((".", ":", "?", "!"))


def clean_text(text):
    text = text.replace("\x7f", "•")

    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()

        if line == "":
            continue  # skip blank lines

        if len(cleaned_lines) > 0 and is_continuation(cleaned_lines[-1], line):
            cleaned_lines[-1] = cleaned_lines[-1] + " " + line
        else:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def load_documents(data_dir: str = None):
    """Load every PDF in the data folder and clean its text."""
    folder = Path(data_dir or config.DATA_DIR)
    documents = []

    for pdf_file in folder.glob("*.pdf"):
        for page in PyPDFLoader(str(pdf_file)).load():
            page.page_content = clean_text(page.page_content)
            documents.append(page)

    # Stop early, otherwise vector_store sync would delete every stored chunk
    if len(documents) == 0:
        raise SystemExit(f"No PDFs found in '{folder}'. Nothing to ingest.")

    return documents
