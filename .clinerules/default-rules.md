# Project Rules

## General Principles

- Do not use cloud AI APIs.
- All inference must run locally.
- Company data must never leave the machine.

## Architecture

- Prefer simple solutions.
- Avoid overengineering.
- Build a working MVP first.

If there is a choice between:
- perfect architecture
- working MVP

Always choose the working MVP.

## Models

- LLM must run via Ollama.
- Models should be configurable via environment variables.

## Code Quality

- Use Python type hints where appropriate.
- Write clear and readable code.
- Add docstrings for major modules.

Avoid:

- overly complex abstractions
- unnecessary layers

## Dependencies

- Only introduce dependencies when necessary.
- Prefer well-maintained libraries.

## Reliability

The system must:

- handle corrupted files
- handle unsupported formats gracefully
- log indexing and retrieval operations

## Documentation

README must always include:

- installation steps
- how to run the system
- how to index documents
- example queries

## Development Process

1. Start with a minimal working system
2. Validate the pipeline
3. Then improve structure and features