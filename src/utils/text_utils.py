import re

def extract_words(text):
    """
    Extract normalized words from text.
    """
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]+\b", text.lower())
    return set(words)


def find_new_terms(source_text, generated_text):
    """
    Find words appearing in generated output but not source.
    """
    source_words = extract_words(source_text)
    generated_words = extract_words(generated_text)

    ignore = {
        "corrective",
        "preventive",
        "actions",
        "lessons",
        "learned",
        "root",
        "cause",
        "analysis",
        "monitoring",
        "review",
        "system",
        "service",
    }

    return sorted(
        list(
            generated_words -
            source_words -
            ignore
        )
    )