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

## Running the Workflow

Once you've configured all the settings:

1. **Review your configuration**
   - Double-check your time range, data source, and event types
   - Verify your output format selections

2. **Save and run**
   - Click the "Save" or "Run Workflow" button in Ecoscope Desktop
   - The workflow will begin processing

3. **Monitor progress**
   - You'll see status updates as the workflow runs
   - Processing time depends on:
     - The size of your date range
     - Number of events in the system
     - Whether you're downloading attachments
     - Whether you're generating maps

4. **Wait for completion**
   - The workflow will notify you when it's finished
   - Check for any error messages if the workflow fails

## Understanding Your Results

After the workflow completes successfully, you'll find your outputs in the designated output folder.

### Data Outputs

Your event data will be saved in the format(s) you selected:

#### CSV Format
- **File extension**: `.csv`
- **Opens in**: Microsoft Excel, Google Sheets, or any spreadsheet application
- **Best for**:
  - Quick data review and analysis
  - Sharing with non-technical users
  - Creating pivot tables and charts
  - Importing into other tools
- **Contents**: All event data in tabular format with one row per event

#### GeoParquet Format
- **File extension**: `.geoparquet` or `.parquet`
- **Opens in**: Python (pandas, geopandas), R, or GIS applications
- **Best for**:
  - Large datasets (more efficient than CSV)
  - Programmatic analysis
  - Preserving geospatial data types
  - Long-term data storage
- **Contents**: Compressed columnar format with full geospatial support

#### GPKG Format (GeoPackage)
- **File extension**: `.gpkg`
- **Opens in**: QGIS, ArcGIS, or other GIS software
- **Best for**:
  - Spatial analysis and mapping
  - Integration with other GIS layers
  - Users familiar with GIS tools
- **Contents**: Geospatial database format with geometry information

### Visual Outputs (When Maps are Generated)

If you didn't skip map generation, you'll also receive:

#### Interactive Map
- **Format**: HTML file or embedded in dashboard
- **Features**:
  - Event points plotted at their locations
  - Points colored by event type (different colors for arrests, snares, camps, etc.)
  - Interactive - click on points to see event details
  - Base map layers you selected (satellite, terrain, etc.)
  - Zoom and pan capabilities

### Grouped Outputs

If you configured data grouping:
- You'll receive separate files for each group
- File naming will indicate the group (e.g., `events_January.csv`, `events_February.csv`)
- Each file contains only the events for that time period or category
- Maps (if generated) will also be separated by group

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
  - Since: `2025-08-01`
  - Until: `2025-08-31`
- **Event Types**: Leave empty (download all types)
- **Event Columns**: Use defaults
- **Filetypes**: Select `CSV`
- **Skip Attachment Download**: Checked
- **Skip Map Generation**: Checked (for faster processing)

**Result**: Single CSV file with all events from August 2025

---

### Example 2: Specific Incident Types with Map
**Goal**: Analyze arrest and snare reports with visual map

**Configuration**:
- **Time Range**: Your desired date range
- **Event Types**: `["arrest_rep", "snare_rep", "poacher_camp_rep"]`
- **Event Columns**:
  - `["id", "time", "event_type", "event_category", "reported_by", "serial_number", "geometry"]`
- **Filetypes**: Select `CSV` and `GPKG`
- **Skip Attachment Download**: Checked
- **Skip Map Generation**: Unchecked

**Result**:
- CSV file for spreadsheet analysis
- GPKG file for GIS analysis
- Interactive map showing arrest and snare locations colored by event type

---

### Example 3: Monthly Grouped Reports
**Goal**: Separate files for each month to track trends over time

**Configuration**:
- **Time Range**:
  - Since: `2025-01-01`
  - Until: `2025-12-31`
- **Event Types**: Leave empty or specify types
- **Group Data**:
  - Select `"%B"` (Month name: January, February, etc.)
- **Filetypes**: Select `CSV`
- **Skip Attachment Download**: Checked

**Result**: 12 separate CSV files, one for each month

---

### Example 4: Detailed Event Report with Photos
**Goal**: Download events with all attachments for documentation

**Configuration**:
- **Time Range**: Your desired date range
- **Event Types**: Specify relevant types
- **Event Columns**: Include `event_details` to get additional information
- **Filetypes**: Select `CSV`
- **Skip Attachment Download**: Unchecked
- **Skip Map Generation**: As needed

**Result**:
- CSV file with detailed event information
- Attachments folder with all photos and documents organized by event ID

---

### Example 5: Filtered Geographic Area
**Goal**: Download only events within a specific region

**Configuration**:
- **Time Range**: Your desired date range
- **Event Types**: As needed
- **Filter Event Relocations** (Advanced):
  - Set **Bounding Box** coordinates for your area of interest
  - Example: Min Longitude: 37.0, Max Longitude: 38.0, Min Latitude: -1.0, Max Latitude: 0.0
- **Filetypes**: Select preferred formats

**Result**: Events only from within your specified geographic boundaries

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
- Enable "Skip Map Generation" for large datasets
- Enable "Skip Attachment Download" if you don't need photos/documents
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
- Ensure "Skip Map Generation" is unchecked
- Verify your events have valid geometry/location data
- Try using default base map settings
