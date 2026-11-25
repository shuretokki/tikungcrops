# SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
# SPDX-License-Identifier: Apache-2.0

"""Reference statistics reader: valid files, spreadsheet exports and every kind of bad row."""

from __future__ import annotations

from pathlib import Path

import pytest

from tikungcrops.pipeline.reference import ReferenceDataError, read_reference, reference_path

HEADER = "unit,year,crop,harvested_area_ha,production_ton,source\n"


def write(aoi, tmp_path: Path, text: str) -> None:
    path = reference_path(aoi, tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")


def test_missing_or_header_only_file_means_no_reference(small_aoi, tmp_path):
    assert read_reference(small_aoi, tmp_path) is None
    write(small_aoi, tmp_path, HEADER)
    assert read_reference(small_aoi, tmp_path) is None


def test_valid_file_normalises_unit_and_crop(small_aoi, tmp_path):
    write(small_aoi, tmp_path, HEADER + "jotosanur,2020,Padi Sawah,459,,bps\nDesa A,2020,padi,120.5,700,bps\n")
    df = read_reference(small_aoi, tmp_path)
    assert df is not None
    assert df["unit"].to_list() == ["Joto Sanur", "Desa A"]
    assert df["crop"].to_list() == ["padi_sawah", "padi"]
    assert df["production_ton"].to_list() == [None, 700.0]


def test_semicolon_export_with_indonesian_numbers(small_aoi, tmp_path):
    write(small_aoi, tmp_path, "﻿unit;year;crop;harvested_area_ha;source\nDesa A;2021;padi;1.234,5;dkpp\n")
    df = read_reference(small_aoi, tmp_path)
    assert df is not None
    assert df["harvested_area_ha"].item() == pytest.approx(1234.5)


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("Desa A,20x0,padi,10,,bps", "`year` is not an integer"),
        ("Desa A,1850,padi,10,,bps", "`year` outside"),
        ("Desa A,2020,padi,-1,,bps", "negative"),
        ("Desa A,2020,padi,ten,,bps", "`harvested_area_ha` is not a number"),
        ("Desa A,2020,padi,10,,", "`source` is empty"),
        ("Desa Z,2020,padi,10,,bps", "unknown unit"),
    ],
)
def test_bad_rows_are_reported_with_line_numbers(small_aoi, tmp_path, row, message):
    write(small_aoi, tmp_path, HEADER + row + "\n")
    with pytest.raises(ReferenceDataError, match=message):
        read_reference(small_aoi, tmp_path)


def test_duplicate_rows_are_rejected(small_aoi, tmp_path):
    write(small_aoi, tmp_path, HEADER + "Desa A,2020,padi,10,,bps\ndesa a,2020,padi,12,,bps\n")
    with pytest.raises(ReferenceDataError, match=r"duplicate .* line\(s\) 2, 3"):
        read_reference(small_aoi, tmp_path)


def test_missing_column_is_named(small_aoi, tmp_path):
    write(small_aoi, tmp_path, "unit,year,crop,source\nDesa A,2020,padi,bps\n")
    with pytest.raises(ReferenceDataError, match="harvested_area_ha"):
        read_reference(small_aoi, tmp_path)
