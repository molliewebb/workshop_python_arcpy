## Create, Manipulate, Extract Spatial Data With Python
## Dependencies: arcpy (installed with ArcGIS Desktop and ArcGIS Pro)
##
## Mollie Webb
## GIS Programmer and Instructor
## Washington University in St. Louis
## molliewebb@wustl.edu

## References
# EPSG Reference - http://spatialreference.org/ref/epsg/
# SR - http://pro.arcgis.com/en/pro-app/arcpy/classes/spatialreference.htm
# STL PD data - https://www.slmpd.org/crime_stats.shtml
# Social Explorer - https://www.socialexplorer.com/ (WashU License)
# Census Blockgroup Shapefiles - https://www.census.gov/geo/maps-data/data/cbf/cbf_blkgrp.html

## ENVIRONMENT SET UP

# Imports libraries
import arcpy
import os
import sys

# Sets Project Directory
path = r"\path\to\project"

# Sets ArcPy environment to overwrite outputs
arcpy.env.overwriteOutput = True

# Sets output geodatabase location and name
gdb_name = "STL_City.gdb"
gdb_path = os.path.join(path,gdb_name)

# Checks if geodatabase exists, if not, creates it
# ArcPy Help - LINK HERE
if arcpy.Exists(gdb_path) == False:
    arcpy.CreateFileGDB_management(path, gdb_name)

# Sets arcpy workspace to the gdb
arcpy.env.workspace = gdb_path

## CODE BLOCK 1 - CREATE FEATURE CLASSES WITH CRIME DATA FROM CSV

# Sets variables related to crime csv files
crime_x_field = "XCoord"
crime_y_field = "YCoord"
crime_spatial_ref = 102696
crime_fc_name = "STL_Crimes"
crime_scrub_fc_name = "STL_Crimes_Scrubbed"

## CODE BLOCK 1a

# Loops through all the files in the project directory
for file in os.listdir(path):
 # Checks if the file is a csv
 if file.endswith(".CSV"):
     # Sets the full path to the file
     file_path = os.path.join(path,file)
     # Sets the output fc name
     fc_name = "Crime_" + file[:-4]
     # Uses the XY To Table tool to create a fc using the location fields
     # ArcPy Help - http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/make-xy-event-layer.htm
     temp = arcpy.MakeXYEventLayer_management(file_path, crime_x_field, crime_y_field, "temp", crime_spatial_ref)
     # Creates a feature class from this temp layer
     # ArcPy Help = http://pro.arcgis.com/en/pro-app/tool-reference/data-management/copy-features.htm
     arcpy.CopyFeatures_management (temp, fc_name)
     del temp

#### CODE BLOCK 1b
##
### Creates a list of the crime feature classes by using a wildcard
### ArcPy Help - http://pro.arcgis.com/en/pro-app/arcpy/functions/listfeatureclasses.htm
##crime_fc_list = arcpy.ListFeatureClasses("Crime*")
##
#### CODE BLOCK 1c
##
### Merges all of the individual crime feature classes to a single crime feature class
### ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/merge.htm
##crime_fc = arcpy.Merge_management (crime_fc_list, crime_fc_name)
##
#### CODE BLOCK 1d
##
### Cleans up crimes feature class by removing rows with zero coordinates
##loc_zero_query = crime_x_field + " > 0 AND " + crime_y_field + " > 0"
### ArcPy Help - http://desktop.arcgis.com/en/arcmap/latest/tools/conversion-toolbox/feature-class-to-feature-class.htm
##crime_scrub_fc = arcpy.FeatureClassToFeatureClass_conversion (crime_fc, gdb_path, crime_scrub_fc_name,loc_zero_query)
##
#### END CODE BLOCK 1

#### CODE BLOCK 2 - CENSUS BLOCK GROUP SHAPES AND DATA TABULAR JOIN
##
### Sets paths to parcel data
##bg_shp = os.path.join (path,r"cb_2017_29_bg_500k.shp")
##bg_tbl = os.path.join(path,"R11920448_SL150.csv")
##
### Sets join field and output fc name and field names
##bg_shp_join_field = "GEOID_NUM"
##bg_tbl_join_field = "Geo_FIPS"
##bg_fc_joined = "STL_BG_Joined"
##bg_fc_name = "STL_BG_Crime_Counts"
##
### Makes a feature layer for the block groups to be used in the join
### ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/make-feature-layer.htm
##bg_lyr = arcpy.MakeFeatureLayer_management(bg_shp,"bg_lyr")
##
### Performs a tabular join between shapes and data table
### ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/add-join.htm
##bg_joined = arcpy.AddJoin_management (bg_lyr, bg_shp_join_field, bg_tbl, bg_tbl_join_field,"KEEP_COMMON")
##
### Exports the joined shapes and table as a feature class
### ArcPy Help - http://desktop.arcgis.com/en/arcmap/latest/tools/conversion-toolbox/feature-class-to-feature-class.htm
##bg_joined_fc = arcpy.FeatureClassToFeatureClass_conversion (bg_joined, gdb_path, bg_fc_joined)
##
### Reprojects block groups to common spatial reference
### ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/project.htm
##bg_crimes = arcpy.Project_management (bg_joined_fc, bg_fc_name, crime_spatial_ref)
##
##
#### END CODE BLOCK 2

## BONUS CODE BLOCK - RETRIEVING A LIST OF UNIQUE CRIME TYPES

## There are over 225 different types of crimes, if we wanted to separate out for different types of crimes
## For brevity sake, we will look for a handful of general crime types
####sc = arcpy.da.SearchCursor(crime_scrub_fc,"Description")
####
####crime_list = []
####
####for s in sc:
####    if s[0] not in crime_list:
####        crime_list.append(s[0])
####
####crime_list.sort()
####
####for c in crime_list:
####    print c
##
## ## END BONUS CODE BLOCK
     
#### CODE BLOCK 3 - Perform spatial query and insert results as values in the attribute table
##
### We want to calculate how many crimes occurred near (within .5 mile) of each block group
##
### Sets value for "near"
##crime_types_list = ["ARSON","BURGLARY","DRUGS","LARCENY","ROBBERY","WEAPONS","FRAUD"]
##near_value_ft = "2640 FEET"
##bg_shp_join_field = "cb_2017_29_bg_500k_GEOID_NUM"
##crimes_desc_field = "Description"
##
### Adds a field to the joined parcels layer to hold crime counts
###ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/add-field.htm
##for crime_type in crime_types_list:
##    if crime_type not in arcpy.ListFields(bg_crimes):
##        arcpy.AddField_management(bg_fc_name,crime_type,"LONG")
##
### Creates an update cursor object on block groups
### Update Cursor will iterate through each feature and retrieve or set values
### Update Cursor will only have access to the attributes that we set as the [PARAMETER NAME]
### Since a 'where_clause' was not provided to filter the features, this Update Cursor will iterate through all features
### ArcPy Help - http://pro.arcgis.com/en/pro-app/arcpy/data-access/updatecursor-class.htm
##bg_uc = arcpy.da.UpdateCursor(bg_crimes,([bg_shp_join_field] + crime_types_list))
##
### Iterates through the features specified in the UpdateCursor
##for bg in bg_uc:
##    # Creates query to isolate the target feature using the HANDLE attribute
##    geoid_query = bg_shp_join_field + " = " + str(bg[0])
##    # Creates a feature layer with a single record for the target parcel
##    # ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/make-feature-layer.htm
##    bg_temp = arcpy.MakeFeatureLayer_management(bg_crimes, "bg_temp", geoid_query)
##    print geoid_query
##    print str(arcpy.GetCount_management(bg_temp)[0])
##                              
##    for crime in crime_types_list:
##        
##        # Creates a query for this type of crime
##        crime_query = crimes_desc_field + " LIKE '%" + crime + "%'"                   
##        # Makes a feature layer for the specific crime type in the scrubbed crime fc
##        # ArcPy Help - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/make-feature-layer.htm
##        crime_lyr = arcpy.MakeFeatureLayer_management(crime_scrub_fc,"crime_lyr",crime_query)
##        # Performs a select by location to select all crimes of this type within the specified distance of the block group
##        # ArcPy Help - http://desktop.arcgis.com/en/arcmap/latest/tools/data-management-toolbox/select-layer-by-location.htm
##        crimes_selected = arcpy.SelectLayerByLocation_management (crime_lyr, "WITHIN_A_DISTANCE", bg_temp, near_value_ft)
##        # Sets a variable to the number of features selected in the crimes fc
##        # ArcPy - http://pro.arcgis.com/en/pro-app/tool-reference/data-management/get-count.htm
##        count = arcpy.GetCount_management(crimes_selected)[0]
##        # Sets the crime count attribute to the count
##        crime_index_num = (crime_types_list.index(crime)+ 1)
##        bg[crime_index_num] = count
##        # Performs the update on the feature class
##        bg_uc.updateRow(bg)
##        del crime_lyr
##
##    del bg_temp
##
#### END CODE BLOCK 3

#### CODE BLOCK 4 ##
##
### Sets name and path to output csv
##output_csv = "STL_BG_Crime_Counts.csv"
##output_path = os.path.join(path,output_csv)
##
### Exports attribute table to csv
### ArcPy Help - LINK HERE
##arcpy.TableToTable_conversion (bg_crimes, path, output_csv)
##
#### END CODE BLOCK 4






























