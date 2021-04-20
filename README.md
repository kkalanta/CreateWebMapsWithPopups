# Create Web Maps with Custom Popups
Current Python script includes steps to create a web map from feature layer collection and define custom popups for operational layers of web map. In addition to HTML format, the popup function uses names or labels of fields in feature layers. It changes the color, font type, and font size of description in popups and defines decimal places and digit separators in numeric fields.

# Python Version
- Python 3.7.9
- ArcGIS API for Python version 1.8.4 (modules of arcgis.gis and arcgis.mapping)

# Script Steps
The script consists of the following steps:
- Establishing a connection to ArcGIS Enterprise/Portal
- Accessing to specified feature layer collection and update its properties
- Creating an empty web map and add feature layers to it
- Defining web map properties
- Creating popups for specified map layers
- Saving the web map on the portal

# Assumptions
There are following assumptions for running the script. 
- It is considered that running this script is a repeating process for various projects. The main differentiation of the projects is their names. The script has three arguments. The first argument is project_name, which is a string and is used to find feature layer collections and name the newly created web maps on the portal. The formats utilized for the names of feature layer collections and web maps are respectively “project_name_Map” and “project_name_WebMap”. The second argument, layer_names is a list of strings for the name of map layers that are supposed to have custom popups. The last argument accepts various number of arguments to be used for the tags of feature layer collections and web maps. 
- The names of fields in feature layers have CamelCase format, for example, “ProjectName”. 
