"""MongoDB aggregation pipelines for the access patterns in the hybrid schema.

Spec: documents/local/skema-hibrida.md section 3.3. Each pipeline starts with
a `$match` on the leading key of its index so the planner can use an IXSCAN
instead of a full collection scan; `explain_stages` reports which one it
picked.

Run `just agg` (or `uv run python -m jotosanur_agri.mongo_agg`) to print every
pipeline's result and plan.
"""

from __future__ import annotations

from typing import Any

from pymongo.collection import Collection
from pymongo.database import Database

from jotosanur_agri.mongo import connect

# BPS renamed the category between editions: "sapi" (2014) vs "sapi_potong" (2021).
JENIS_SAPI = ["sapi", "sapi_potong"]


def produksi_per_tahun_pipeline(komoditas: list[str]) -> list[dict[str, Any]]:
    """A1: real (non-synthetic) production per commodity and year.

    Productivity is recomputed as total production over total area, so large
    villages weigh more than small ones. Averaging per-village ratios would not.

    Args:
        komoditas: Commodities to include, e.g. ``["padi", "jagung_hibrida"]``.

    Returns:
        The aggregation pipeline.
    """
    return [
        {"$match": {"komoditas": {"$in": komoditas}, "sumber.is_synthetic": False}},
        {
            "$group": {
                "_id": {"komoditas": "$komoditas", "tahun": "$periode.tahun"},
                "lokasi": {"$sum": 1},
                "luas_ha": {"$sum": "$luas_ha"},
                "produksi_ton": {"$sum": "$produksi_ton"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "komoditas": "$_id.komoditas",
                "tahun": "$_id.tahun",
                "lokasi": 1,
                "luas_ha": {"$round": ["$luas_ha", 2]},
                "produksi_ton": {"$round": ["$produksi_ton", 2]},
                "produktivitas_ton_per_ha": {
                    "$cond": [
                        {"$gt": ["$luas_ha", 0]},
                        {"$round": [{"$divide": ["$produksi_ton", "$luas_ha"]}, 2]},
                        None,
                    ]
                },
            }
        },
        {"$sort": {"komoditas": 1, "tahun": 1}},
    ]


def deret_panen_pipeline(komoditas: str, lokasi: str) -> list[dict[str, Any]]:
    """A2: harvest series for one commodity at one location, oldest first.

    Args:
        komoditas: Commodity, e.g. ``"padi"``.
        lokasi: ``lokasi.nama``, e.g. a plot id such as ``"P01"``.

    Returns:
        The aggregation pipeline.
    """
    return [
        {"$match": {"komoditas": komoditas, "lokasi.nama": lokasi}},
        {"$sort": {"periode.tanggal_panen": 1}},
        {
            "$project": {
                "_id": 1,
                "tanggal_panen": "$periode.tanggal_panen",
                "siklus_ke": "$periode.siklus_ke",
                "produktivitas_ton_per_ha": 1,
                "is_synthetic": "$sumber.is_synthetic",
            }
        },
    ]


def tren_ternak_pipeline(jenis_ternak: list[str], lokasi: str) -> list[dict[str, Any]]:
    """A3: livestock headcount over time at one location.

    Args:
        jenis_ternak: Livestock categories to include.
        lokasi: ``lokasi.nama``, e.g. ``"Jotosanur"``.

    Returns:
        The aggregation pipeline.
    """
    return [
        {"$match": {"jenis_ternak": {"$in": jenis_ternak}, "lokasi.nama": lokasi}},
        {"$sort": {"tanggal": 1}},
        {
            "$project": {
                "_id": 0,
                "tanggal": 1,
                "jenis_ternak": 1,
                "jumlah_ekor": 1,
                "sumber": "$sumber.kode",
            }
        },
    ]


def ringkasan_sumber_pipeline() -> list[dict[str, Any]]:
    """A4: document count per source, synthetic vs real.

    No index by design: the collection is small and `sumber.kode` has low
    cardinality, so this is expected to be a COLLSCAN.

    Returns:
        The aggregation pipeline.
    """
    return [
        {"$group": {"_id": {"kode": "$sumber.kode", "is_synthetic": "$sumber.is_synthetic"}, "dokumen": {"$sum": 1}}},
        {"$project": {"_id": 0, "sumber": "$_id.kode", "is_synthetic": "$_id.is_synthetic", "dokumen": 1}},
        {"$sort": {"sumber": 1}},
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
    # Fully pushed-down pipelines report queryPlanner at the top level;
    # others nest it under the first stage's $cursor.
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
    """The four access patterns, keyed by their spec id, with example arguments."""
    return {
        "A1 produksi per komoditas per tahun (riil)": (
            db["panen"],
            produksi_per_tahun_pipeline(["padi", "jagung_hibrida"]),
        ),
        "A2 deret panen padi plot P01": (db["panen"], deret_panen_pipeline("padi", "P01")),
        "A3 tren sapi Jotosanur": (db["ternak"], tren_ternak_pipeline(JENIS_SAPI, "Jotosanur")),
        "A4 dokumen per sumber": (db["panen"], ringkasan_sumber_pipeline()),
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
