# EarthRanger Events Download Workflow

## Introduction

This workflow allows you to download and analyze event data from EarthRanger.

**What this workflow does:**
- Downloads event data from EarthRanger for a specified time period
- Filters and processes events based on your criteria
- Exports data in multiple formats (CSV, Parquet)
- Optionally creates visual maps showing event locations, including polygon events
  (e.g. project boundaries, fire perimeters) rendered as filled polygon layers
- Optionally downloads attachments (photos, documents) associated with events

**Who should use this:**
- Conservation managers analyzing incident patterns
- Field coordinators preparing reports
- Data analysts extracting event data for further analysis
- Anyone needing to export EarthRanger event data in a structured format

## Prerequisites

Before using this workflow, you need:

1. **Ecoscope Desktop** installed on your computer
   - If you haven't installed it yet, please follow the installation instructions for Ecoscope Desktop

2. **EarthRanger Data Source** configured in Ecoscope Desktop
   - You must have already set up a connection to your EarthRanger server
   - Your data source should be configured with proper authentication credentials
   - You'll need to know the name of your configured data source (e.g., "mep_dev")

## Installation

1. Open Ecoscope Desktop
2. Select "Workflow Templates"
3. Click "+ Add Template"
4. Copy and paste this URL https://github.com/wildlife-dynamics/wt-download-events and wait for the workflow template to be downloaded and initialized
5. The template will now appear in your available template list

## Configuration Guide

Once you've added the workflow template, you'll need to configure it for your specific needs. The configuration form is organized into the following sections, in order. Some sections expose extra fields under an **"Advanced Configurations"** accordion.

#### 1. Workflow Details
Give your workflow a name and description to help you identify it later.

- **Workflow Name** (required): A descriptive name for this workflow run and the dashboard title
  - Example: `"August 2015 Events"`
- **Workflow Description** (optional): Additional details about this analysis
  - Example: `"Download arrest and snare events for monthly report"`

#### 2. Data Source
Select your EarthRanger connection.

- **Data Source** (required): Choose from your configured data sources
  - Example: Select `mep_dev` from the dropdown

#### 3. Time Range
Specify the time period for the events you want to download.

- **Timezone** (required): Use the dropdown to select your timezone
- **Since** (required): Use the calendar picker to select the start date and time
  - Example: `12/17/2025, 12:00 AM`
- **Until** (required): Use the calendar picker to select the end date and time
  - Example: `12/18/2025, 12:00 AM`

#### 4. Event Types
Choose which events to download.

- **Event Types**: Specify which event types to include. You can find them on your earthranger site: https://<your-site>.pamdas.org/admin/activity/eventtype/ and use the value here.
  - Leave empty to download all event types
  - Example: `["arrest_rep", "snare_rep", "poacher_camp_rep"]`
- **Include events without a location**: Events without coordinates (point or area) will still appear in your download.
  - Default: checked
- **Simplify polygons to single points**: Converts polygon events to their center point. Leave unchecked to keep original shapes in maps and exports.
  - Default: unchecked (polygon events are preserved as polygons)

Note: The workflow automatically fetches all available columns and processes event details (mapping coded values to their display titles). You can control which columns appear in your final output using **Remove Columns** in the **Refine Data** section.

#### 5. Event Location Filter (Optional)
Optionally limit events to a geographic area, and exclude events recorded at specific coordinates (for example, known placeholder points like 0, 0). Leave empty to keep all events.

- **Bounding Box**: Limit events to a geographic area
  - Default: entire world (-180 to 180 longitude, -90 to 90 latitude)
- **Filter Exact Point Coordinates**: Exclude events at specific coordinates
  - Useful for filtering out test data or GPS outliers
  - Example: `[{"Latitude": 0.0, "Longitude": 0.0}, {"Latitude": 180.0, "Longitude": 90.0}]`

#### 6. Group Data (Optional)
Specify how the data should be grouped to create separate views for your dashboard (optional). Leave empty to show all data in a single view.

- **Group by**: Create separate outputs grouped by:
  - Time: Year, Month, Day of week, Hour, etc.
  - Category: Select a categorical column from your event data (e.g., event_type, event_category). If you're unsure which columns are available, run the workflow once without grouping to see the data, then configure grouping in a subsequent run.

#### 7. Refine Data
Reshape and organize your data before downloading. This section has two steps:

- **Remove Columns**: Columns listed here will be left out of your download. The list is pre-filled with columns that are typically unnecessary or duplicated; modify it based on your requirements. **Remove Columns applies to both your downloaded files and the generated map.**
  - Default includes common internal/system columns: `location`, `end_time`, `message`, `provenance`, `attributes`, `comment`, `patrol_segments`, `updated_at`, `is_contained_in`, `sort_at`, `icon_id`, `url`, `image_url`, `geojson`, `related_subjects`, `patrols`, `reported_by`
- **Custom Data Query (SQL Query)**: Write a SQL query to filter or transform your data. Leave blank to skip this step.
  - Use `df` as the table name. Example: `SELECT * FROM df WHERE status = 'active'`
  - **The query applies only to your downloaded files, not the generated map.** (See [Maps vs. downloads](#maps-vs-downloads) below.)

#### 8. Download File Format
Choose how to save your data.

- **Filetype**: Select one or more output formats
  - **CSV**: Standard spreadsheet format, opens in Excel. Geometry is written as
    Well-Known Text (WKT) — readable but not directly round-trippable into all
    GIS tools.
  - **Parquet (GeoParquet)** (recommended for polygon events): Efficient format for
    geospatial data; preserves all geometry types natively (Point, Polygon,
    MultiPolygon). [Learn more about GeoParquet](https://geoparquet.org/).
  - Example: Select both `CSV` and `Parquet`
- **Filename Prefix** (optional): Custom prefix for output files. Ecoscope will attach a hash code to keep it unique
  - Default: `"events"`
  - Example: `"events_monthly"` will create files like `events_monthly_abc123.csv`

#### 9. Download Attachments
Control whether to download files attached to events (photos, documents, etc.). All the files will be stored under `<output_folder>/attachments/<event_id>`.

- **Download all attachments**:
  - Check this to download all attachments associated with the events
  - Default: unchecked (attachments are not downloaded)

#### 10. Generate Maps
Control whether to create map visualizations.

- **Generate maps in dashboard**: Helper text: *Not recommended for large datasets.*
  - Default: checked (maps are generated)
  - Uncheck to skip map generation (faster for large datasets)
- **Map Base Layers** (Advanced): Customize the background maps for your visualizations.
  - Available options: Open Street Map, Roadmap, Satellite, Terrain, or custom layers with a URL
  - Default: Terrain and Satellite layers
  - The first layer will appear on the bottom

<a name="maps-vs-downloads"></a>
> **Maps vs. downloads.** Grouping/splitting happens **before** the refine step, then the
> pipeline forks: **Remove Columns** runs before the fork, so it affects **both** the map and
> your downloaded files. **Custom Data Query (SQL)** runs only on the downloads branch — it
> shapes your **downloaded files but never the map**. This means you can aggregate or drop
> columns in SQL for your exports while the dashboard map still renders normally. Maps are
> always colored consistently by event type, regardless of grouping.

## Running the Workflow

Once you've configured all the settings:

1. **Review your configuration**
   - Double-check your time range, data source, and event types

2. **Save and run**
   - Click the "Submit" and the workflow will show up in "My Workflows" table button in Ecoscope Desktop
   - Click on "Run" and the workflow will begin processing

3. **Monitor progress and wait for completion**
   - You'll see status updates as the workflow runs
   - Processing time depends on:
     - The size of your date range
     - The number of events in the system for that range
     - Whether attachment download and map generation are enabled
   - The workflow completes with status "Success" or "Failed"

## Understanding Your Results

After the workflow completes successfully, you'll find your outputs in the designated output folder.

### Data Outputs

Your event data will be saved in the format(s) you selected:
- **File formats**: CSV and/or Parquet (based on your selection)
- **Opens in**: Microsoft Excel, Google Sheets (CSV), Python/R (Parquet)
- **Best for**:
  - CSV: Quick data review and analysis
  - Parquet: Large datasets with spatial data, programmatic analysis, efficient storage
- **Contents**: All event data with normalized event details (coded values are automatically mapped to human-readable display titles), minus any columns you set in **Remove Columns** and reflecting any **Custom Data Query** you ran

### Visual Outputs (When Maps are Generated)

If you left **Generate maps in dashboard** checked, you'll also receive:

#### Interactive Map
- **Format**: HTML file or embedded in dashboard
- **Features**:
  - Event points plotted at their locations, with polygon events rendered as
    filled polygon layers in the same color scheme. When both geometry types
    are present, polygons are drawn underneath with point markers on top.
  - Points and polygons colored by event type (different colors for arrests,
    snares, camps, project boundaries, etc.)
  - Interactive - click on points or polygons to see event details
  - Base map layers you selected (satellite, terrain, etc.)
  - Zoom and pan capabilities

### Grouped Outputs

If you configured data grouping:
- You'll receive separate files for each group. Each file contains only the events for that time period or category
- Maps (if generated) will also be separated by group, with each group view selectable in the dashboard

### Attachments (If Downloaded)

If you enabled attachment downloads:
- **Location**: `<output_folder>/attachments/<event_id>/`
- **Organization**: Each event's attachments stored in its own folder
- **File types**: Photos (JPG, PNG), documents (PDF), or other files uploaded to EarthRanger
- **Naming**: Original filenames preserved

## Common Use Cases & Examples

Here are some typical scenarios and how to configure the workflow for each:

### Example 1: Simple Monthly Report
**Goal**: Download all events for a specific month to review in Excel

**Configuration**:
- **Time Range**:
  - Since: `2025-08-01T00:00:00`
  - Until: `2025-08-31T23:59:59`
  - Timezone: `Africa/Nairobi (UTC+03:00)`
- **Event Types**: Leave empty (download all types)
- **Filetype**: Select `CSV`
- **Download all attachments**: Unchecked (default)
- **Generate maps in dashboard**: Unchecked (for faster processing)

**Result**: Single CSV file with all events from August 2025

---

### Example 2: Specific Incident Types with Map
**Goal**: Analyze arrest and snare reports with visual map

**Configuration**:
- **Time Range**: Your desired date range
- **Event Types**: `["arrest_rep", "snare_rep", "poacher_camp_rep"]`
- **Filetype**: Select `CSV` and `Parquet`
- **Download all attachments**: Unchecked (default)
- **Generate maps in dashboard**: Checked (default)

**Result**:
- CSV file for spreadsheet analysis
- Parquet file for programmatic analysis
- Interactive map showing arrest and snare locations colored by event type

---

### Example 3: Monthly Grouped Reports
**Goal**: Separate files for each month to track trends over time

**Configuration**:
- **Time Range**:
  - Since: `2025-01-01T00:00:00`
  - Until: `2025-12-31T23:59:59`
  - Timezone: `Africa/Nairobi (UTC+03:00)`
- **Event Types**: Leave empty or specify types
- **Group Data**:
  - Select `"%B"` (Month name: January, February, etc.)
- **Filetype**: Select `CSV`
- **Download all attachments**: Unchecked (default)

**Result**: 12 separate CSV files, one for each month

---

### Example 4: Detailed Event Report with Photos
**Goal**: Download events with all attachments for documentation

**Configuration**:
- **Time Range**: Your desired date range
- **Event Types**: Specify relevant types
- **Filetype**: Select `CSV`
- **Download all attachments**: Checked
- **Generate maps in dashboard**: As needed

**Result**:
- CSV file with detailed event information (event details are automatically expanded into separate columns with human-readable values)
- Attachments folder with all photos and documents organized by event ID

---

### Example 5: Mixed Point and Polygon Events
**Goal**: Download events that include polygon geometries (e.g. project
boundaries, fire perimeters) alongside point events, and visualize both on
a single map.

**Configuration**:
- **Time Range**: Your desired date range
- **Event Types**: Include both point and polygon event types
  (e.g. `["arrest_rep", "arr_project_boundary"]`)
- **Simplify polygons to single points**: Unchecked (preserve polygons)
- **Filetype**: Select `Parquet` (recommended for polygon geometry)
- **Generate maps in dashboard**: Checked (default)

**Result**:
- Parquet file with mixed Point and Polygon geometry rows
- Interactive map with point markers drawn on top of filled polygon layers,
  both colored by event type

---

### Example 6: Filtered Geographic Area
**Goal**: Download only events within a specific region

**Configuration**:
- **Time Range**: Your desired date range
- **Event Types**: As needed
- **Event Location Filter**:
  - Set **Bounding Box** coordinates for your area of interest
  - Example: Min Longitude: 37.0, Max Longitude: 38.0, Min Latitude: -1.0, Max Latitude: 0.0
- **Filetype**: Select preferred formats

**Result**: Events only from within your specified geographic boundaries

---

### Example 7: Aggregated Export with a Map
**Goal**: Produce an aggregated summary table for download while still seeing the
individual events on the dashboard map.

**Configuration**:
- **Time Range**: Your desired date range
- **Event Types**: As needed
- **Refine Data → Custom Data Query**:
  - Example: `SELECT event_type, DATE(event_time) AS event_time, COUNT(*) AS n FROM df GROUP BY event_type, DATE(event_time)`
- **Filetype**: Select `CSV`
- **Generate maps in dashboard**: Checked (default)

**Result**:
- A CSV with one aggregated row per event type per day (the SQL result)
- An interactive map that still shows every individual event — the query applies
  only to the downloaded file, not the map

## Troubleshooting

### Common Issues and Solutions

#### Workflow fails to start
**Problem**: The workflow won't run or immediately fails

**Solutions**:
- Verify your EarthRanger data source is properly configured
- Check that you have network connectivity to the EarthRanger server
- Ensure your credentials haven't expired
- Confirm the data source name matches exactly.

#### No events returned
**Problem**: Workflow completes but produces empty results

**Solutions**:
- Verify the date range is correct (start date should be before end date)
- Check that the event types you specified actually exist in your EarthRanger system. Make sure you are using `VALUE`, not `DISPLAY`
- Visit `https://<your-site>.pamdas.org/admin/activity/eventtype/` to confirm event type names
- Remove any filters temporarily to see if they're excluding all data
- Try a broader date range to verify events exist

#### Workflow runs very slowly
**Problem**: The workflow takes an extremely long time to complete

**Solutions**:
- Uncheck "Generate maps in dashboard" for large datasets
- Leave "Download all attachments" unchecked if you don't need photos/documents
- Reduce the date range to smaller time periods
- Limit the number of event types selected
- Process data in smaller batches (by month or quarter)
- The first run may take longer as the environment gets warmed up. The following ones should be faster.

#### Authentication errors
**Problem**: Errors related to login or permissions

**Solutions**:
- Re-configure your EarthRanger data source in Ecoscope Desktop
- Verify your user account has permission to access event data in EarthRanger

#### Map won't generate
**Problem**: Data downloads successfully but no map is created

**Solutions**:
- Ensure "Generate maps in dashboard" is checked
- Verify your events have valid geometry/location data
- If you used a **Custom Data Query**, remember it does not affect the map — check that your events have geometry rather than the query
- Try using default base map settings
