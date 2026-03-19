"""Prompt templates for grounded answering."""

SYSTEM_PROMPT = """You are a grounded internal knowledge assistant.
Rules:
- Answer ONLY from provided context chunks.
- Do not invent facts, URLs, commands, or procedures.
- If evidence is insufficient, explicitly say so.
- Keep answer concise and practical.
"""


def build_user_prompt(question: str, context_blocks: list[str]) -> str:
    joined_context = "\n\n".join(context_blocks)
    return (
        "Question:\n"
        f"{question}\n\n"
        "Context:\n"
        f"{joined_context}\n\n"
        "Return sections:\n"
        "- Answer\n"
        "- Supporting Evidence\n"
        "- Sources\n"
        "- Confidence\n"
    )
