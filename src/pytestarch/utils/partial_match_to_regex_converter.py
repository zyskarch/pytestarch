from __future__ import annotations

import re

REGEX_ALL_MARKER = ".*"
PARTIAL_MATCH_ALL_MARKER = "*"


def convert_partial_match_to_regex(match: str) -> str:
    """Partial match strings can only have the form of *text*, where the leading and trailing * are optional. Text is
    a regular string that will be matched character by character against another string.

    Args:
        match: string in the format of a partial match string

    Returns:
        Regex version of the partial match string. This means that the partial match characters * have been replaced
        by their regex equivalent .* and the rest of the string has been escaped to not contain any characters that
        have a special meaning in a regex. In addition, $ will be added at the end if no * was present their before.
        This is done because partial matches are used as full string matches, unless * is present at the end.
    """
    all_at_start = match.startswith(PARTIAL_MATCH_ALL_MARKER)
    all_at_end = match.endswith(PARTIAL_MATCH_ALL_MARKER)

    match_length = len(match)

    start_index = 1 if all_at_start else 0
    end_index = match_length - 1 if all_at_end else match_length

    match_without_markers = match[start_index:end_index]

    escaped = re.escape(match_without_markers)

    if all_at_start:
        escaped = f"{REGEX_ALL_MARKER}{escaped}"

    if all_at_end:
        escaped = f"{escaped}{REGEX_ALL_MARKER}"
    else:
        escaped = f"{escaped}$"

    return escaped
