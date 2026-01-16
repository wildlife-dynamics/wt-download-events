# EarthRanger Events Download Workflow

## Introduction

This workflow allows you to download and analyze event data from EarthRanger.

**What this workflow does:**
- Downloads event data from EarthRanger for a specified time period
- Filters and processes events based on your criteria
- Exports data in multiple formats (CSV, GeoParquet, GPKG)
- Optionally creates visual maps showing event locations
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
4. Copy and paste this URL https://github.com/wildlife-dynamics/wt-download-events and wait for the workflow to be downloaded and initialized
5. The workflow will now appear in your available template list

## Configuration Guide

Once you've added the workflow template, you'll need to configure it for your specific needs. The configuration form is organized into several sections.

### Basic Configuration

These are the essential settings you'll need to configure for every workflow run:

#### 1. Workflow Details
Give your workflow a name and description to help you identify it later.

- **Workflow Name** (required): A descriptive name for this workflow run and the dashboard title
  - Example: `"August 2015 Events"`
- **Workflow Description** (optional): Additional details about this analysis
  - Example: `"Download arrest and snare events for monthly report"`

#### 2. Time Range
Specify the time period for the events you want to download.

- **Timezone**(required): Use the dropdown to select your timezone
- **Since** (required): Use the calendar picker to select the start date and time
  - Example: `12/17/2025, 12:00 AM`
- **Until** (required): Use the calendar picker to select the end date and time
  - Example: `12/18/2025, 12:00 AM`

#### 3. Data Source
Select your EarthRanger connection.

- **Data Source** (required): Choose from your configured data sources
  - Example: Select `mep_dev` from the dropdown

#### 4. Get Event Data
Choose which events and columns to download.

- **Event Types**: Specify which event types to include. You can find them on your earthranger site: https://<your-site>.pamdas.org/admin/activity/eventtype/ and use the value here.
  - Leave empty to download all event types
  - Example: `["arrest_rep", "snare_rep", "poacher_camp_rep"]`
- **Event Columns**: Select the data fields you want
  - Default includes: id, time, event_type, event_category, title, reported_by, created_at, serial_number, is_collection, event_details, geometry
  - Common columns: `id`, `time`, `event_type`, `event_category`, `reported_by`, `serial_number`, `geometry`
  - Include `event_details` if you need additional event-specific information

#### 5. Download Attachments
Control whether to download files attached to events (photos, documents, etc.). All the files will be stored under <output_folder>/attachments/<event_id>

- **Skip Attachment Download**:
  - Check this to skip downloading attachments (default: checked)
  - Uncheck to download all attachments

##### 6. Group Data
Organize your data into separate views based on time periods or categories.

- **Group by**: Create separate outputs grouped by:
  - Time: Year, Month, Day of week, Hour, etc.
  - Category: Select a categorical column from your event data (e.g., event_type, event_category). If you're unsure which columns are available, run the workflow once without grouping to see the data, then configure grouping in a subsequent run.

#### 7. Persist Events
Choose how to save your data.

- **Filetypes**: Select one or more output formats
  - **CSV**: Standard spreadsheet format, opens in Excel
  - **GeoParquet**: Efficient format for geospatial data
  - **GPKG**: GeoPackage format, opens in GIS software like QGIS
  - Example: Select both `CSV` and `GeoParquet`
- **Filename Prefix** (optional): Custom prefix for output files. Ecoscope will attach a hash code to keep it unique
  - Default: `"events"`
  - Example: `"events_monthly"` will create files like `events_monthly_abc123.csv`


#### 8. Generate Maps

##### Skip Map Generation
Control whether to create map visualizations.

- **Skip**: Check this to skip map generation
  - Recommended for large datasets to improve performance
  - Default: unchecked (maps will be generated)

### Advanced Configuration

These optional settings provide additional control over your workflow:


#### Process Events

##### Filter Event Relocations
Remove unwanted data points from your results.

- **Bounding Box**: Limit events to a geographic area
  - Default: entire world (-180 to 180 longitude, -90 to 90 latitude)
- **Filter Exact Point Coordinates**: Exclude events at specific coordinates
  - Useful for filtering out test data or invalid locations
  - Example: `[{"x": 0.0, "y": 0.0}, {"x": 180.0, "y": 90.0}]`

##### Process Columns
Customize which columns appear in your output.

- **Drop Columns**: Remove specific columns you don't need
  - Example: `["icon_id", "url"]`
- **Retain Columns**: Keep only specific columns in a specific order
  - Leave empty to keep all columns
  - Example: `["time", "event_type", "geometry"]`
- **Rename Columns**: Change column names
  - Example: Rename `reported_by` to `reporter`

##### Apply SQL Query
Advanced users can filter or transform data using SQL.

- **Query**: Write a SQL query to filter or modify the data
  - Use `df` as the table name
  - Example: `SELECT * FROM df WHERE event_category = 'security'`
  - Leave empty to skip


#### Map Base Layers
Customize the background maps for your visualizations.

- **Base Maps**: Select one or more base layers
  - Available options: Open Street Map, Roadmap, Satellite, Terrain, etc.
  - Default: Terrain and Satellite layers
  - The first layer will appear on the bottom