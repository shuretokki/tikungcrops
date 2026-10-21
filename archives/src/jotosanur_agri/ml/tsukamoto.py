# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Generic Tsukamoto fuzzy inference engine.

Used for rice yield (`predict_panen_tsukamoto`) but not tied to that domain.

Tsukamoto requires every rule consequent to be a fuzzy set with a monotonic
membership function (Kusumadewi, 2010). Each rule's crisp output z then follows
algebraically from its fire strength alpha, with no aggregate-then-centroid step as
in Mamdani. The system output is the alpha-weighted mean of the rules' z.

Unlike the random-forest baselines, nothing here is fitted to data: the rule base
comes from expert knowledge and sourced ranges. That makes it the only prediction
component built specifically for Kampung Pandu Sakti (the CIMMYT model is real data
from elsewhere; the synthetic baseline is circular). See `proposal.typ` and
documents/local/adr-integrasi-data-cimmyt.md.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class Monotonicity(Enum):
    """Direction of an output fuzzy set; selects the z-from-alpha formula."""

    INCREASING = "increasing"
    DECREASING = "decreasing"


def shoulder_left(a: float, b: float) -> Callable[[float], float]:
    """Left shoulder: 1 up to `a`, falling linearly to 0 at `b`. For LOW-type sets."""

    def membership(x: float) -> float:
        if x <= a:
            return 1.0
        if x >= b:
            return 0.0
        return (b - x) / (b - a)

    return membership


def shoulder_right(a: float, b: float) -> Callable[[float], float]:
    """Right shoulder: 0 up to `a`, rising linearly to 1 at `b`. For HIGH-type sets."""

    def membership(x: float) -> float:
        if x <= a:
            return 0.0
        if x >= b:
            return 1.0
        return (x - a) / (b - a)

    return membership


def triangular(a: float, b: float, c: float) -> Callable[[float], float]:
    """Triangle: 0 outside (`a`, `c`), peaking at 1 at `b`. For a MEDIUM set between shoulders."""

    def membership(x: float) -> float:
        if x <= a or x >= c:
            return 0.0
        if x <= b:
            return (x - a) / (b - a)
        return (c - x) / (c - b)

    return membership


@dataclass(frozen=True)
class FuzzySet:
    """Fuzzy set of an input variable; any membership shape is allowed."""

    name: str
    membership: Callable[[float], float]


@dataclass(frozen=True)
class OutputFuzzySet:
    """Monotonic fuzzy set of the output variable, i.e. a rule consequent.

    Stored as a direction plus domain bounds rather than a membership function, so
    `crisp_value` can invert it algebraically.
    """

    name: str
    monotonicity: Monotonicity
    domain_min: float
    domain_max: float

    def crisp_value(self, alpha: float) -> float:
        """Return the z at which this set's membership equals `alpha`."""
        span = self.domain_max - self.domain_min
        if self.monotonicity is Monotonicity.INCREASING:
            return self.domain_min + alpha * span
        return self.domain_max - alpha * span


@dataclass(frozen=True)
class FuzzyVariable:
    """Input variable with its named fuzzy sets, e.g. LOW and HIGH."""

    name: str
    sets: dict[str, FuzzySet]

    def fuzzify(self, x: float) -> dict[str, float]:
        """Membership degree of `x` in each set, keyed by set name."""
        return {set_name: fuzzy_set.membership(x) for set_name, fuzzy_set in self.sets.items()}


@dataclass(frozen=True)
class OutputVariable:
    """The single output variable and its monotonic sets."""

    name: str
    sets: dict[str, OutputFuzzySet]


@dataclass(frozen=True)
class Rule:
    """One IF-THEN rule. Antecedents combine with AND, evaluated as MIN.

    Attributes:
        antecedents: Set name per input variable, e.g.
            ``{"dosis_pupuk_kg_ha": "RENDAH", "dosis_bibit_kg_ha": "TINGGI"}``.
        consequent: Name of a set in `OutputVariable.sets`.
    """

    antecedents: dict[str, str]
    consequent: str


@dataclass(frozen=True)
class RuleResult:
    """A rule's alpha and z for one input."""

    rule: Rule
    alpha: float
    z: float


@dataclass(frozen=True)
class InferenceResult:
    """System output plus every rule's alpha and z."""

    output: float
    rule_results: list[RuleResult]

    def trace(self) -> str:
        """One line per rule with alpha > 0; rules at alpha = 0 do not affect the output."""
        active = [r for r in self.rule_results if r.alpha > 0]
        if not active:
            return "  (no active rules)"
        return "\n".join(
            (
                f"  {' AND '.join(f'{var}={set_name}' for var, set_name in r.rule.antecedents.items())}"
                + f" -> {r.rule.consequent}: alpha={r.alpha:.3f}, z={r.z:.2f}"
            )
            for r in active
        )


class TsukamotoSystem:
    """Fuzzification, MIN rule evaluation and weighted-average defuzzification."""

    def __init__(self, inputs: list[FuzzyVariable], output: OutputVariable, rules: list[Rule]) -> None:
        """Index the inputs by name.

        Args:
            inputs: Input variables.
            output: The output variable; every rule consequent must name one of its sets.
            rules: The rule base.
        """
        self.inputs: dict[str, FuzzyVariable] = {variable.name: variable for variable in inputs}
        self.output: OutputVariable = output
        self.rules: list[Rule] = rules

    def infer(self, values: dict[str, float]) -> InferenceResult:
        """Run one prediction.

        Args:
            values: Crisp value per input variable name.

        Returns:
            The weighted-average output and the per-rule breakdown.

        Raises:
            ValueError: If every rule has alpha = 0, i.e. no rule covers the input.
        """
        memberships = {name: variable.fuzzify(values[name]) for name, variable in self.inputs.items()}

        rule_results: list[RuleResult] = []
        for rule in self.rules:
            alpha = min(memberships[variable][set_name] for variable, set_name in rule.antecedents.items())
            z = self.output.sets[rule.consequent].crisp_value(alpha)
            rule_results.append(RuleResult(rule=rule, alpha=alpha, z=z))

        denominator = sum(r.alpha for r in rule_results)
        if denominator == 0:
            raise ValueError(f"all alpha-predicates are 0, no rule covers the input: {values}")

        numerator = sum(r.alpha * r.z for r in rule_results)
        return InferenceResult(output=numerator / denominator, rule_results=rule_results)
