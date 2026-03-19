# Generation Layer Workflow

## Goal
Generate grounded answers using Ollama and retrieved evidence.

## Files

### `app/generation/ollama_client.py`
Responsibilities:
- call Ollama generation endpoint,
- send prompts and context,
- handle model failures,
- expose configurable model settings.

### `app/generation/prompts.py`
Responsibilities:
- define system prompt,
- define answer format instructions,
- define source citation requirements,
- define fallback behavior instructions.

Prompt requirements:
- answer only from supplied context,
- do not invent commands, URLs, or procedures,
- say when evidence is insufficient,
- preserve source metadata.

### `app/generation/answer_builder.py`
Responsibilities:
- build generation input from user question and retrieved chunks,
- build final answer payload,
- append sources,
- compute confidence label,
- produce UI-ready output.

## Required Answer Sections
- Answer
- Supporting Evidence
- Sources
- Confidence

## Confidence Rules
Possible values:
- High
- Medium
- Low
- Insufficient evidence

## Required Behavior
- If retrieval is strong, generate a grounded answer.
- If retrieval is weak, skip generation or constrain it into a fallback response.
- Never produce unsupported operational instructions.

## Deliverable
Implement a grounded generation pipeline that always includes source attribution or explicit fallback.