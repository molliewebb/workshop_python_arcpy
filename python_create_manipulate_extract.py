## Working with Spatial Data in Python

## Dependencies: arcpy (installed with ArcGIS Desktop and ArcGIS Pro)
## Note: ArcGIS Desktop (ArcMap) will install Python 2.7.x
## Note: ArcGIS Pro will install Python 3.x

## WORKSHOP INSTRUCTOR - Mollie Webb
# GIS Programmer
# Washington University in St. Louis
# molliewebb@wustl.edu

## WORKFLOW
# This script imports CSV files that contain crime data with locations from St. Louis City.
# The location data is used to create spatial (points feature classes) data
# for each CSV file and then uses the Merge tool to combine the feature class
# and the Project tool to change the spatial reference
# Next, a tabular join is performed between Census block groups and tabular data
# from Social Explorer.  Then the script uses an Update Cursor and Select by Location
# tool to count the number of crimes of different types near each block group.
# Finally, the attribute table of the resulting feature class is exported to a CSV.

## REFERENCES
# EPSG guide - https://spatialreference.org/ref/epsg/
# SR - http://pro.arcgis.com/en/pro-app/arcpy/classes/spatialreference.htm
# STL PD data - https://www.slmpd.org/crime_stats.shtml
# Social Explorer - https://www.socialexplorer.com/ (WashU License)
# Census Blockgroup Shapefiles - https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html

## PROJECT/WORKSHOP SET UP - TO DO LIST:
# If not using a lab machine, you must have ArcGIS Desktop (ArcMap) or ArcGIS Pro installed
# Download workshop files from Github repo - https://github.com/molliewebb/workshop_python_arcpy
# Unzip the downloaded .zip file
# Unzip the block group shapefile - cb_2017_29_bg_500k.zip - into the workshop directory

## ENVIRONMENT SET UP

# Imports libraries
import arcpy
import os

# Sets Project Directory
#path = r"\path\to\project"

# Sets ArcPy environment to overwrite outputs
arcpy.env.overwriteOutput = True

# Sets output geodatabase location and name
gdb_name = "STL_City.gdb"
gdb_path = os.path.join(path,gdb_name)

# Checks if geodatabase exists, if not, creates it
# ArcPy Help - https://pro.arcgis.com/en/pro-app/tool-reference/data-management/create-file-gdb.htm
if arcpy.Exists(gdb_path) == False:
    arcpy.CreateFileGDB_management(path, gdb_name)
    print(gdb_name + " has been created")
else:
    print(gdb_name + " already exists")

# Sets arcpy workspace to the gdb
arcpy.env.workspace = gdb_path

## Setting Variables - Code Block 1

# Sets variables related to crime csv files
crime_x_field = "XCoord"
crime_y_field = "YCoord"
crime_type_field = "Description"
# This EPSG code is for State Plane Missouri East
# See p.7 of the STL Crime FAQ - https://www.slmpd.org/Crime/CrimeDataFrequentlyAskedQuestions.pdf
crime_spatial_ref = 102696
crime_fc_name = "STL_Crimes"
crime_scrub_fc_name = "STL_Crimes_Scrubbed"

## Setting Variables - Code Block 2

# Sets paths to parcel data
# Make sure block group shapefile has been unzipped
bg_shp_file = r"cb_2017_29_bg_500k.shp"
bg_tbl_file = r"R11920448_SL150.csv"
bg_shp = os.path.join (path,bg_shp_file)
bg_tbl = os.path.join(path,bg_tbl_file)

# Sets join field and output fc name and field names
bg_shp_join_field = "GEOID_NUM"
bg_tbl_join_field = "Geo_FIPS"
bg_shp_id_field = "GEOID"
bg_fc_id_field = bg_shp_file[:-4] + "_" + bg_shp_id_field
bg_fc_name = "STL_BG_Crime_Counts"
bg_fc_state_plane_name = "STL_BG_Crime_Counts_SP_MO_East"

## Setting Variables - Code Block 3

# There are over 225 different types of crimes, if we wanted to separate out for different types of crimes
# For brevity sake, we will look for a few general crime types
crime_types_list = ["ARSON","BURGLARY"]
# Sets value for "near"
near_value_ft = "2640 FEET"

## CODE BLOCK 1 - CREATE FEATURE CLASSES WITH CRIME DATA FROM CSV

## CODE BLOCK 1a

##### Loops through all the files in the project directory
####for file in os.listdir(path):
#### # Checks if the file is a csv
#### if file.endswith(".CSV"):
####     # Sets the full path to the file
####     file_path = os.path.join(path,file)
####     # Sets the output fc name, the name of the file minus the last 4 characters
####     fc_name = "Crime_" + file[:-4]
####     # Uses the XY To Table tool to create a fc using the location fields
####     # ArcPy Help - http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/make-xy-event-layer.htm
####     temp = arcpy.MakeXYEventLayer_management(file_path, crime_x_field, crime_y_field, "temp", crime_spatial_ref)
####     # Creates a feature class from this temp layer
####     # ArcPy Help = http://pro.arcgis.com/en/pro-app/tool-reference/data-management/copy-features.htm
####     arcpy.CopyFeatures_management (temp, fc_name)
####     print(fc_name + " feature class created")
####     del temp

## CODE BLOCK 1b

##### Creates a list of the crime feature classes by using a wildcard
##### ArcPy Help - http://pro.arcgis.com/en/pro-app/arcpy/functions/listfeatureclasses.htm
####crime_fc_list = arcpy.ListFeatureClasses("Crime*")
####
##### Merges all of the individual crime feature classes to a single crime feature class
##### ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/merge.htm
####crime_fc = arcpy.Merge_management (crime_fc_list, crime_fc_name)
####print(crime_fc_name + " feature class created using Merge tool")

## CODE BLOCK 1c

##### Referencing the merged feature class here since it has already been created in Code Block 1b
####crime_fc = os.path.join(gdb_path,crime_fc_name)
##### Cleans up crimes feature class by removing rows with zero coordinates
####loc_zero_query = crime_x_field + " > 0 AND " + crime_y_field + " > 0"
####print(loc_zero_query)
##### ArcPy Help - http://desktop.arcgis.com/en/arcmap/latest/tools/conversion-toolbox/feature-class-to-feature-class.htm
####crime_scrub_fc = arcpy.FeatureClassToFeatureClass_conversion (crime_fc, gdb_path, crime_scrub_fc_name,loc_zero_query)
####print(crime_scrub_fc_name + " feature class created")

## END CODE BLOCK 1

## CODE BLOCK 2 - CENSUS BLOCK GROUP SHAPES AND DATA TABULAR JOIN and RE-PROJECT

##### Makes a feature layer for the block groups to be used in the join
##### ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/make-feature-layer.htm
####bg_lyr = arcpy.MakeFeatureLayer_management(bg_shp,"bg_lyr")
####
##### Performs a tabular join between shapes and data table
##### ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/add-join.htm
####bg_joined = arcpy.AddJoin_management (bg_lyr, bg_shp_join_field, bg_tbl, bg_tbl_join_field,"KEEP_COMMON")
####print("Block group shapes and block group tabular data have been joined")
####
##### Exports the joined shapes and table as a feature class
##### ArcPy Help - http://desktop.arcgis.com/en/arcmap/latest/tools/conversion-toolbox/feature-class-to-feature-class.htm
####bg_joined_fc = arcpy.FeatureClassToFeatureClass_conversion (bg_joined, gdb_path, bg_fc_name)
####print(bg_fc_name + " feature class has been created")
####
##### Reprojects the joined block groups into the same projection as the crime points
##### ArcPy Help - https://pro.arcgis.com/en/pro-app/tool-reference/data-management/project.htm
####bg_projected_fc = arcpy.Project_management(bg_joined_fc, bg_fc_state_plane_name, crime_spatial_ref)
####print(bg_fc_state_plane_name + " projected feature class has been created")

## END CODE BLOCK 2

## CODE BLOCK 3 - Perform spatial query and insert results as values in the attribute table
## Script will calculate how many crimes occurred near (within .5 mile) of each block group
## Insert the count as a value for each crime type for reach block group feature

##### Referencing the scrubbed crime feature class and projected feature class
##### here since they were already created in Code Block 1b
####crime_scrub_fc = os.path.join(gdb_path,crime_scrub_fc_name)
####bg_projected_fc = os.path.join(gdb_path, bg_fc_state_plane_name)
####
##### Adds fields to the joined bg layer to hold crime counts
##### ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/add-field.htm
####for crime_type in crime_types_list:
####    if crime_type not in arcpy.ListFields(bg_projected_fc):
####        arcpy.AddField_management(bg_projected_fc,crime_type,"LONG")
####
##### Makes a feature layer for the scrubbed crime fc, to be used in  the select by location operation
##### ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/make-feature-layer.htm
####crime_scrub_lyr = arcpy.MakeFeatureLayer_management(crime_scrub_fc,"crime_scrub_lyr")
####
##### Loop through each crime type
####for crime_type in crime_types_list:
####    
####    # Creates an update cursor object on parcels
####    # Update Cursor will iterate through each feature and retrieve or set values
####    # Update Cursor will only have access to the attributes that we set as the "field_names" parameter
####    # If a "where_clause" parameter is not provided, the Update Cursor will iterate through all features
####    # ArcPy Help - https://pro.arcgis.com/en/pro-app/arcpy/data-access/updatecursor-class.htm
####    bg_uc = arcpy.da.UpdateCursor(bg_projected_fc,[bg_fc_id_field,crime_type])
####    # The bg_shp_join_field will be the first element in the cursor result [0]
####    # The specific crime count attribute will be the second element in the cursor result [1]
####    print("Working on " + crime_type + " counts")
####
####    # Iterates through the features specified in the UpdateCursor
####    for bg in bg_uc:
####     # Creates query to isolate the target feature using the ID
####     bg_query = bg_fc_id_field + " = '" + str(bg[0]) + "'"
####     # Creates a feature layer with a single record for the target bg
####     # ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/make-feature-layer.htm
####     bg_temp = arcpy.MakeFeatureLayer_management (bg_projected_fc, "bg_temp", bg_query)
####     # Performs a select by location to select all crimes within the specified distance of the parcel
####     # ArcPy Help - https://pro.arcgis.com/en/pro-app/tool-reference/data-management/select-layer-by-location.htm
####     crimes_selected = arcpy.SelectLayerByLocation_management (crime_scrub_lyr, "WITHIN_A_DISTANCE", bg_temp, near_value_ft)
####     #Creates a query to isolate only the crimes of the specific type "crime_type"
####     crime_type_query = crime_type_field + " LIKE '" + crime_type + "%'"
####     # Performs a select by attribute on the already selected crimes (within the specified distance)
####     crimes_selected_by_type = arcpy.SelectLayerByAttribute_management(crimes_selected,"SUBSET_SELECTION",crime_type_query)
####     # Sets a variable to the count of features selected in the crimes fc
####     # ArcPy Help - https://pro.arcgis.com/en/pro-app/tool-reference/data-management/get-count.htm
####     count = arcpy.GetCount_management(crimes_selected_by_type)[0]
####     # Sets the crime count attribute to the count
####     bg[1] = count
####     # Performs the update on the feature class
####     bg_uc.updateRow(bg)
####     # Clears the selected crime features and deletes the feature layer
####     arcpy.SelectLayerByAttribute_management(crime_scrub_lyr,"CLEAR_SELECTION")
####     del bg_temp

## END CODE BLOCK 3

#### CODE BLOCK 4 - EXPORT RESULTS TO A TABLE ##

## It may be necessary to export the attribute table of the resulting feature
## class to a CSV for import into another application (e.g. for statistical analysis)

##### Sets name and path to output csv
####output_csv = "STL_BG_Crime_Counts.csv"
####output_path = os.path.join(path,output_csv)
##### Referencing the completed block group feature class
####bg_projected_fc = os.path.join(gdb_path, bg_fc_state_plane_name)
####
##### Exports attribute table to csv
##### ArcPy Help - https://pro.arcgis.com/en/pro-app/tool-reference/conversion/table-to-table.htm
####arcpy.TableToTable_conversion (bg_projected_fc, path, output_csv)
####print("The table " + output_csv + " has been created")

#### END CODE BLOCK 4
