"""
Generates the fixture used by the sql-explode test case:

  - process-events-details-explode.example-return.parquet
      Mock for ecoscope_workflows_ext_custom.tasks.io.process_events_details
      (the last io-tagged node in the prep chain, so under mock_io: true its
      example_return clobbers everything upstream). Schema mirrors the bundled
      process-events-details.example-return.parquet plus a `species_observed`
      column holding a JSON-encoded array string, so the SQL step has a real
      array to explode via SQLite's json_each().

`species_observed` is a JSON *string* (e.g. '["lion", "zebra"]'), not a Python
list: the released apply_sql_query task hands columns straight to SQLite via
pandasql, which rejects native list/tuple/ndarray cells. A JSON string stores
cleanly and json_each() parses it back into one row per element.

Re-run this script (instead of editing the parquet by hand) if the upstream
process_events_details schema changes.
"""
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

OUT = Path(__file__).parent / "process-events-details-explode.example-return.parquet"

# One list value per row, of varying length, so the explode fans 4 input rows
# into 1 + 2 + 3 + 1 = 7 output rows. Every row has >= 1 element so no event
# silently drops out of the json_each inner join.
rows = [
    {
        "id": "00000000-0000-0000-0000-0000000000a1",
        "time": "2015-01-03T08:00:00Z",
        "event_type": "elephant_sigthing_test",
        "event_category": "wildlife",
        "geometry": Point(38.733, -2.386),
        "serial_number": "201",
        "event_type_display": "Elephant Sighting Test",
        "event_details": {"Herd Type": "Bull Only"},
        "reported_by_name": "eco_1",
        "species_observed": json.dumps(["elephant"]),
    },
    {
        "id": "00000000-0000-0000-0000-0000000000a2",
        "time": "2015-01-04T09:30:00Z",
        "event_type": "wildlife_sighting_rep",
        "event_category": "wildlife",
        "geometry": Point(38.74, -2.39),
        "serial_number": "202",
        "event_type_display": "Wildlife Sighting",
        "event_details": {"Herd Type": "Mixed"},
        "reported_by_name": "eco_1",
        "species_observed": json.dumps(["lion", "zebra"]),
    },
    {
        "id": "00000000-0000-0000-0000-0000000000a3",
        "time": "2015-01-05T14:15:00Z",
        "event_type": "wildlife_sighting_rep",
        "event_category": "wildlife",
        "geometry": Point(38.75, -2.40),
        "serial_number": "203",
        "event_type_display": "Wildlife Sighting",
        "event_details": {"Herd Type": "Mixed"},
        "reported_by_name": "eco_2",
        "species_observed": json.dumps(["buffalo", "wildebeest", "gazelle"]),
    },
    {
        "id": "00000000-0000-0000-0000-0000000000a4",
        "time": "2015-01-06T16:00:00Z",
        "event_type": "elephant_sigthing_test",
        "event_category": "wildlife",
        "geometry": Point(38.76, -2.41),
        "serial_number": "204",
        "event_type_display": "Elephant Sighting Test",
        "event_details": {"Herd Type": "Bull Only"},
        "reported_by_name": "eco_2",
        "species_observed": json.dumps(["elephant"]),
    },
]

df = pd.DataFrame(rows)
df["time"] = pd.to_datetime(df["time"], utc=True)
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
gdf.to_parquet(OUT, index=False)
print(f"wrote {OUT} ({len(gdf)} rows; species_observed explodes to 7)")
