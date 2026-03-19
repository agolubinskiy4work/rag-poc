# Source Attribution and Fallback Workflow

## Goal
Define rules for citations and "I don't know" behavior.

## Source Attribution Rules
Every successful answer must include a Sources section.

Each citation should contain:
- title
- URL or file path
- optional section title
- optional short snippet

Rules:
- cite only documents actually used in the final response,
- do not fabricate missing URLs,
- if multiple chunks come from one document, group them where appropriate,
- preserve transcript file names when no URL exists.

## Fallback Rules
Use fallback when:
- no strong retrieval results exist,
- evidence is weak or ambiguous,
- top chunks are not sufficient to answer the question,
- sources conflict and cannot be reconciled confidently.

## Fallback Output Shape
- explicit statement that the system could not answer confidently,
- brief reason,
- optional related sources section.

## Example Fallback
I could not find enough reliable evidence in the indexed sources to answer this confidently.

Related sources:
- ...
- ...

## Confidence Labels
- High
- Medium
- Low
- Insufficient evidence

## Deliverable
Apply attribution and fallback logic consistently in retrieval and generation outputs.