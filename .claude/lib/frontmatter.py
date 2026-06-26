"""Shared YAML frontmatter parser.

Extracts YAML frontmatter from markdown files using PyYAML.
Used by graph_builder.py and mempalace_client.py.
"""
from __future__ import annotations

import logging
import re
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content.

    Returns (frontmatter_dict, body_text).
    On any parse error, returns ({}, full_content).
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}, content

    fm_text, body = match.group(1), match.group(2)

    try:
        fm = yaml.safe_load(fm_text)
        if isinstance(fm, dict):
            return fm, body
    except yaml.YAMLError as exc:
        logger.warning("frontmatter YAML parse error: %s", exc)

    return {}, content
