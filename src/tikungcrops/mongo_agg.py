# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""MongoDB aggregation pipelines for the dashboard and API access patterns.

Each pipeline starts with a `$match` on the leading key of its index (see
`mongo.INDEXES`) so the planner can use an IXSCAN instead of a full collection scan.
`explain_stages` reports which one it picked.

Run `just agg` (or `uv run python -m tikungcrops.mongo_agg`) to print every
pipeline's result and plan.
"""

from __future__ import annotations

from typing import Any

from pymongo.collection import Collection
from pymongo.database import Database

from tikungcrops.mongo import connect


def production_by_year_pipeline(commodities: list[str]) -> list[dict[str, Any]]:
    """A1: real (non-synthetic) production per commodity and year.

    Yield is recomputed as total production over total area, so large villages weigh
    more than small ones. Averaging per-village ratios would not.

    Args:
        commodities: Commodities to include, e.g. ``["padi", "jagung_hibrida"]``.

    Returns:
        The aggregation pipeline.
    """
    return [
        {"$match": {"commodity": {"$in": commodities}, "source.is_synthetic": False}},
        {
            "$group": {
                "_id": {"commodity": "$commodity", "year": "$period.year"},
                "locations": {"$sum": 1},
                "area_ha": {"$sum": "$area_ha"},
                "production_ton": {"$sum": "$production_ton"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "commodity": "$_id.commodity",
                "year": "$_id.year",
                "locations": 1,
                "area_ha": {"$round": ["$area_ha", 2]},
                "production_ton": {"$round": ["$production_ton", 2]},
                "yield_ton_per_ha": {
                    "$cond": [
                        {"$gt": ["$area_ha", 0]},
                        {"$round": [{"$divide": ["$production_ton", "$area_ha"]}, 2]},
                        None,
                    ]
                },
            }
        },
        {"$sort": {"commodity": 1, "year": 1}},
    ]


def harvest_series_pipeline(commodity: str, location: str) -> list[dict[str, Any]]:
    """A2: harvest series for one commodity at one location, oldest first.

    Args:
        commodity: Commodity, e.g. ``"padi"``.
        location: ``location.name``, e.g. a village such as ``"Jotosanur"`` or a partner plot.

    Returns:
        The aggregation pipeline.
    """
    return [
        {"$match": {"commodity": commodity, "location.name": location}},
        {"$sort": {"period.harvest_date": 1}},
        {
            "$project": {
                "_id": 1,
                "year": "$period.year",
                "harvest_date": "$period.harvest_date",
                "cycle": "$period.cycle",
                "yield_ton_per_ha": 1,
                "is_synthetic": "$source.is_synthetic",
            }
        },
    ]


def unit_seasons_pipeline(aoi: str, unit: str) -> list[dict[str, Any]]:
    """A4: satellite planting seasons of one AOI unit, oldest first.

    Args:
        aoi: AOI slug, e.g. ``"idn-jawatimur-lamongan-tikung"``.
        unit: Unit name, e.g. ``"Jotosanur"``.

    Returns:
        The aggregation pipeline.
    """
    return [
        {"$match": {"aoi": aoi, "unit": unit}},
        {"$sort": {"year": 1, "season": 1}},
        {
            "$project": {
                "_id": 0,
                "year": 1,
                "season": 1,
                "area_ha": {"$round": ["$area_ha", 1]},
                "rice_area_ha": {"$round": ["$rice_area_ha", 1]},
                "flooding_median": "$flooding.median",
                "harvest_median": "$harvest.median",
            }
        },
    ]


def source_summary_pipeline() -> list[dict[str, Any]]:
    """A3: document count per source, synthetic vs real.

    No index by design: the collection is small and `source.code` has low
    cardinality, so this is expected to be a COLLSCAN.

    Returns:
        The aggregation pipeline.
    """
    return [
        {"$group": {"_id": {"code": "$source.code", "is_synthetic": "$source.is_synthetic"}, "documents": {"$sum": 1}}},
        {"$project": {"_id": 0, "source": "$_id.code", "is_synthetic": "$_id.is_synthetic", "documents": 1}},
        {"$sort": {"source": 1}},
    ]


def explain_stages(collection: Collection, pipeline: list[dict[str, Any]]) -> list[str]:
    """List the plan stages MongoDB picked for a pipeline.

    Args:
        collection: Collection the pipeline runs on.
        pipeline: The aggregation pipeline.

    Returns:
        Stage names in the winning plan, outermost first, e.g.
        ``["FETCH", "IXSCAN"]`` or ``["COLLSCAN"]``.
    """
    plan = collection.database.command(
        "explain",
        {"aggregate": collection.name, "pipeline": pipeline, "cursor": {}},
        verbosity="queryPlanner",
    )
    # fully pushed-down pipelines report queryPlanner at the top level,
    # others nest it under the first stage's $cursor
    planner = plan.get("queryPlanner") or plan["stages"][0]["$cursor"]["queryPlanner"]
    winning = planner["winningPlan"]
    return _stage_names(winning.get("queryPlan", winning))


def _stage_names(node: dict[str, Any]) -> list[str]:
    names = [node["stage"]] if "stage" in node else []
    for child in (node.get("inputStage"), *node.get("inputStages", [])):
        if child:
            names += _stage_names(child)
    return names


def queries(db: Database) -> dict[str, tuple[Collection, list[dict[str, Any]]]]:
    """The access patterns A1-A4, with example arguments."""
    return {
        "A1 production per commodity and year (real)": (
            db["harvests"],
            production_by_year_pipeline(["padi", "jagung_hibrida"]),
        ),
        "A2 rice harvest series, Jotosanur": (db["harvests"], harvest_series_pipeline("padi", "Jotosanur")),
        "A3 documents per source": (db["harvests"], source_summary_pipeline()),
        "A4 satellite planting seasons, Jotosanur": (
            db["planting_seasons"],
            unit_seasons_pipeline("idn-jawatimur-lamongan-tikung", "Jotosanur"),
        ),
    }


def main() -> None:
    """Print each pipeline's plan stages and results."""
    for title, (collection, pipeline) in queries(connect()).items():
        rows = list(collection.aggregate(pipeline))
        print(f"== {title}")
        print(f"   plan: {' -> '.join(explain_stages(collection, pipeline))}, {len(rows)} rows")
        for row in rows[:10]:
            print(f"   {row}")
        if len(rows) > 10:
            print(f"   ... {len(rows) - 10} more")


if __name__ == "__main__":
    main()
