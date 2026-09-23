"""Tsukamoto system for Kampung Pandu Sakti rice yield (engine: `tsukamoto`).

Status v1: the ranges and rules are initial assumptions from general agronomy and
the sourced data available, not calibrated on Kampung Pandu Sakti's own records,
which do not exist yet (data/raw/sumber-data/README.md section 2). Revise when the
mitra shares operational data, an extension officer (PPL) validates the dosage
ranges, or harvests logged through the dashboard accumulate.

Ranges:
    - dosis_pupuk_kg_ha, 100-350 kg/ha aggregate NPK: general Indonesian paddy
      recommendation (Permentan, extension guidance); not checked against local practice.
    - dosis_bibit_kg_ha, 15-40 kg/ha: generic range for direct-seeded or transplanted
      paddy; the PMJ01 planting method is unconfirmed.
    - produktivitas_ton_ha, 4.0-10.0 t/ha: the lower anchor sits below BPS Tikung 2013
      (6.82 t/ha, pre-program, README section 7); the upper leaves room for PMJ01,
      reported as higher-yielding (README section 2).

Rules follow Liebig's law of the minimum: yield is capped by the scarcest input, so
LOW fertiliser or LOW seed caps yield at LOW, and only HIGH and HIGH give HIGH. This
is a 4-rule (2 variables x 2 sets) simplification of the 8-16 rule schemes in papers
such as Lasut et al. (2024).
"""

from __future__ import annotations

from functools import cache
from typing import Any

from jotosanur_agri.ml.tsukamoto import (
    FuzzySet,
    FuzzyVariable,
    Monotonicity,
    OutputFuzzySet,
    OutputVariable,
    Rule,
    TsukamotoSystem,
    shoulder_left,
    shoulder_right,
)

PUPUK_RENDAH_TINGGI_CROSSOVER = (150.0, 300.0)  # kg/ha, crossover between LOW-falling and HIGH-rising
BIBIT_RENDAH_TINGGI_CROSSOVER = (20.0, 35.0)  # kg/ha
PRODUKTIVITAS_DOMAIN = (4.0, 10.0)  # ton/ha, see source rationale in the module docstring


@cache
def build_padi_tsukamoto() -> TsukamotoSystem:
    """Build the 2-input, 4-rule rice system once; it is immutable, so later calls reuse it."""
    dosis_pupuk = FuzzyVariable(
        name="dosis_pupuk_kg_ha",
        sets={
            "RENDAH": FuzzySet("RENDAH", shoulder_left(*PUPUK_RENDAH_TINGGI_CROSSOVER)),
            "TINGGI": FuzzySet("TINGGI", shoulder_right(*PUPUK_RENDAH_TINGGI_CROSSOVER)),
        },
    )
    dosis_bibit = FuzzyVariable(
        name="dosis_bibit_kg_ha",
        sets={
            "RENDAH": FuzzySet("RENDAH", shoulder_left(*BIBIT_RENDAH_TINGGI_CROSSOVER)),
            "TINGGI": FuzzySet("TINGGI", shoulder_right(*BIBIT_RENDAH_TINGGI_CROSSOVER)),
        },
    )

    domain_min, domain_max = PRODUKTIVITAS_DOMAIN
    produktivitas = OutputVariable(
        name="produktivitas_ton_ha",
        sets={
            "RENDAH": OutputFuzzySet("RENDAH", Monotonicity.DECREASING, domain_min, domain_max),
            "TINGGI": OutputFuzzySet("TINGGI", Monotonicity.INCREASING, domain_min, domain_max),
        },
    )

    rules = [
        Rule({"dosis_pupuk_kg_ha": "RENDAH", "dosis_bibit_kg_ha": "RENDAH"}, "RENDAH"),
        Rule({"dosis_pupuk_kg_ha": "RENDAH", "dosis_bibit_kg_ha": "TINGGI"}, "RENDAH"),
        Rule({"dosis_pupuk_kg_ha": "TINGGI", "dosis_bibit_kg_ha": "RENDAH"}, "RENDAH"),
        Rule({"dosis_pupuk_kg_ha": "TINGGI", "dosis_bibit_kg_ha": "TINGGI"}, "TINGGI"),
    ]

    return TsukamotoSystem(inputs=[dosis_pupuk, dosis_bibit], output=produktivitas, rules=rules)


def predict_produktivitas(dosis_pupuk_kg_ha: float, dosis_bibit_kg_ha: float) -> dict[str, Any]:
    """Predict rice yield from fertilizer and seed dosage.

    Args:
        dosis_pupuk_kg_ha: Aggregate NPK dosage, kg/ha.
        dosis_bibit_kg_ha: Seed dosage, kg/ha.

    Returns:
        `produktivitas_ton_ha` (float) and `trace` (str): alpha and z of each active
        rule, shown on the dashboard so the prediction is not a black box.
    """
    result = build_padi_tsukamoto().infer(
        {"dosis_pupuk_kg_ha": dosis_pupuk_kg_ha, "dosis_bibit_kg_ha": dosis_bibit_kg_ha}
    )
    return {"produktivitas_ton_ha": result.output, "trace": result.trace()}


if __name__ == "__main__":
    # low/low, mixed, high/high
    scenarios = [
        (100.0, 15.0),
        (150.0, 35.0),
        (300.0, 35.0),
    ]
    for pupuk, bibit in scenarios:
        hasil = predict_produktivitas(pupuk, bibit)
        print(f"pupuk={pupuk} kg/ha, bibit={bibit} kg/ha -> produktivitas={hasil['produktivitas_ton_ha']:.2f} ton/ha")
        print(hasil["trace"])
        print()
