"""Prompt injection defense + response shape validation + secret masking.

Rev 2.1 Security Addendum: S1 (sanitize), S2 (shape check), S6 (secret masking).
Defends rerank LLM against injection attacks in mined session log bodies.
"""
from __future__ import annotations

import json
import re

MAX_BODY_LEN = 500

# Regex patterns for injection markers (role markers + common injection phrases)
_INJECTION_TAG_PATTERNS = [
    re.compile(r"<SYSTEM>(.*?)</SYSTEM>", re.DOTALL | re.IGNORECASE),
    re.compile(r"\[INST\](.*?)\[/INST\]", re.DOTALL | re.IGNORECASE),
    re.compile(r"<\|im_start\|>system", re.IGNORECASE),
    re.compile(r"<\|im_end\|>", re.IGNORECASE),
]

_INJECTION_PHRASE_PATTERNS = [
    # English
    re.compile(r"ignore\s+(?:the\s+)?(?:previous|prior|above)\s+(?:instructions?|directions?|prompts?)", re.IGNORECASE),
    re.compile(r"disregard\s+(?:the\s+)?(?:previous|prior|above)", re.IGNORECASE),
    re.compile(r"new\s+(?:directive|instruction|system\s+prompt)", re.IGNORECASE),
    re.compile(r"forget\s+(?:everything|all)\s+(?:above|prior|previous)", re.IGNORECASE),
    # Korean
    re.compile(r"이전\s*지시\s*무시"),
    re.compile(r"위\s*지시\s*무시"),
    re.compile(r"새\s*지시"),
]

REDACTED = "[REDACTED_INSTRUCTION]"


def sanitize_snippet_for_rerank(body: str) -> str:
    """Neutralize injection markers in a candidate body before sending to rerank LLM.

    - Replace <SYSTEM>...</SYSTEM>/[INST]...[/INST]/<|im_start|>... role markers
      with [REDACTED_INSTRUCTION] (whole match, including inner content)
    - Replace English/Korean 'ignore previous instructions'-class phrases with [REDACTED_INSTRUCTION]
    - Truncate to MAX_BODY_LEN (500) chars to limit the attack window
    """
    if not body:
        return ""
    result = body

    # Replace role marker tags including inner content
    for pattern in _INJECTION_TAG_PATTERNS:
        result = pattern.sub(REDACTED, result)

    # Replace injection phrases
    for pattern in _INJECTION_PHRASE_PATTERNS:
        result = pattern.sub(REDACTED, result)

    # Truncate
    if len(result) > MAX_BODY_LEN:
        result = result[:MAX_BODY_LEN]

    return result


def assert_response_shape(
    raw_response: str, expected_ids: set[str]
) -> list[str] | None:
    """Validate rerank LLM response. Returns list[str] of IDs or None on any failure.

    Rules:
    - Must parse as JSON array
    - Each element must be a string
    - Element count must be <= len(expected_ids)
    - Every element must be in expected_ids (no hallucinated IDs)
    - Any violation → return None (caller falls back to original order)
    """
    if not isinstance(raw_response, str):
        return None
    try:
        parsed = json.loads(raw_response)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(parsed, list):
        return None
    if len(parsed) > len(expected_ids):
        return None
    result: list[str] = []
    for item in parsed:
        if not isinstance(item, str):
            return None
        if item not in expected_ids:
            return None
        result.append(item)
    return result


def has_injection_markers(text: str) -> bool:
    """Quick detection helper for tests and logging. Returns True if any marker matches."""
    if not text:
        return False
    for pattern in _INJECTION_TAG_PATTERNS:
        if pattern.search(text):
            return True
    for pattern in _INJECTION_PHRASE_PATTERNS:
        if pattern.search(text):
            return True
    return False


def mask_secret(text: str, secrets: dict[str, str]) -> str:
    """Replace every occurrence of each secret value in `text` with ***REDACTED***.

    secrets: {name: value} — typically {"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY")}
    Empty or None values are skipped.
    """
    if not text:
        return text
    result = text
    for name, value in secrets.items():
        if value and isinstance(value, str) and len(value) >= 4:
            result = result.replace(value, "***REDACTED***")
    return result
