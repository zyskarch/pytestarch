"""Helpers shared by the experimental predefined architecture rules."""

from __future__ import annotations

from collections.abc import Callable

from pytestarch.eval_structure.evaluable_architecture import EvaluableArchitecture


def assert_applies_with_violation_summary(
    apply_rules: Callable[[EvaluableArchitecture], None],
    evaluable: EvaluableArchitecture,
    architecture: object,
) -> None:
    """Applies the given rules to the evaluable, re-raising any violation with
    a summary of the architecture that was violated.

    Args:
        apply_rules: applies the rules to the evaluable, e.g. the
            'assert_applies' method of a rule applier.
        evaluable: module dependency structure to compare the rules against.
        architecture: object whose string description is prefixed to the error
            message of a violated architecture.

    Raises:
        AssertionError: with an aggregated error message if the rules are
            violated by the evaluable.
    """
    try:
        apply_rules(evaluable)
    except AssertionError as error:
        # the aggregated violations already contain all information needed
        # to fix the architecture, so suppress the internal traceback to
        # avoid printing the violations twice
        raise AssertionError(f"{architecture} was violated:\n{error}") from None
