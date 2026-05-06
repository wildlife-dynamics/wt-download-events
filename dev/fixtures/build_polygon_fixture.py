"""
Generates two mock fixtures used by the polygon-events test case:

  - get-events-polygon.example-return.parquet
      Mock for ecoscope.platform.tasks.io.get_events. Schema mirrors the
      platform's get-events.example-return.parquet.

  - process-events-details-polygon.example-return.parquet
      Mock for ecoscope_workflows_ext_custom.tasks.io.process_events_details.
      The custom-ext task is also tagged "io", so under mock_io: true its own
      example_return clobbers anything upstream of it. We override it with a
      schema that mirrors the upstream get_events fixture plus the columns
      this task is expected to add (event_details, reported_by_name).

Both fixtures together preserve our 5 mixed-geometry rows end-to-end through
the mocked pipeline. Re-run this script (instead of editing the parquets by
hand) if upstream schemas change.
"""
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon

OUT_GET_EVENTS = Path(__file__).parent / "get-events-polygon.example-return.parquet"
OUT_PROCESS = Path(__file__).parent / "process-events-details-polygon.example-return.parquet"

reporter = {
    "additional": {"region": None},
    "common_name": None,
    "content_type": "observations.subject",
    "country": None,
    "created_at": "2024-09-11T00:33:02.966380Z",
    "id": "0f0d79a4-5b35-4057-b5a9-d4329d6566a5",
    "image_url": "/static/ranger-black.svg",
    "is_active": True,
    "name": "eco_1",
    "region": None,
    "sex": None,
    "subject_subtype": "ranger",
    "subject_type": "person",
    "tracks_available": False,
    "updated_at": "2024-09-11T00:33:02.966415Z",
    "user": None,
}

rows = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "time": "2026-01-03T08:00:00Z",
        "event_type": "arr_project_boundary",
        "event_category": "monitoring",
        "reported_by": reporter,
        "geometry": Polygon([(36.80, -1.30), (36.85, -1.30), (36.85, -1.25), (36.80, -1.25)]),
        "serial_number": "1001",
        "event_type_display": "Project Boundary",
    },
    {
        "id": "00000000-0000-0000-0000-000000000002",
        "time": "2026-01-05T10:30:00Z",
        "event_type": "arr_project_boundary",
        "event_category": "monitoring",
        "reported_by": reporter,
        "geometry": Polygon(
            [(36.90, -1.35), (36.95, -1.35), (36.96, -1.31), (36.93, -1.29), (36.89, -1.32)]
        ),
        "serial_number": "1002",
        "event_type_display": "Project Boundary",
    },
    {
        "id": "00000000-0000-0000-0000-000000000003",
        "time": "2026-01-07T14:15:00Z",
        "event_type": "wildlife_sighting_rep",
        "event_category": "wildlife",
        "reported_by": reporter,
        "geometry": Point(36.82, -1.28),
        "serial_number": "1003",
        "event_type_display": "Wildlife Sighting",
    },
    {
        "id": "00000000-0000-0000-0000-000000000004",
        "time": "2026-01-09T09:45:00Z",
        "event_type": "wildlife_sighting_rep",
        "event_category": "wildlife",
        "reported_by": reporter,
        "geometry": Point(36.93, -1.33),
        "serial_number": "1004",
        "event_type_display": "Wildlife Sighting",
    },
    {
        "id": "00000000-0000-0000-0000-000000000005",
        "time": "2026-01-12T16:00:00Z",
        "event_type": "wildlife_sighting_rep",
        "event_category": "wildlife",
        "reported_by": reporter,
        "geometry": None,
        "serial_number": "1005",
        "event_type_display": "Wildlife Sighting",
    },
]

df = pd.DataFrame(rows)
df["time"] = pd.to_datetime(df["time"], utc=True)
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
gdf.to_parquet(OUT_GET_EVENTS, index=False)
print(f"wrote {OUT_GET_EVENTS} ({len(gdf)} rows: 2 Polygon, 2 Point, 1 null)")

# process_events_details mock: same rows, drop `reported_by`, add the
# columns this task contributes downstream (event_details, reported_by_name).
processed = gdf.drop(columns=["reported_by"]).copy()
processed["event_details"] = [{"note": "polygon fixture"} for _ in range(len(processed))]
processed["reported_by_name"] = "eco_1"
processed.to_parquet(OUT_PROCESS, index=False)
print(f"wrote {OUT_PROCESS} ({len(processed)} rows)")
