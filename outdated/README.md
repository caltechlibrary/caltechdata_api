# caltechdata_api outdated functions

These functions have yet to be updated to the InvenioRDM version of
CaltechDATA. Many will be updated in the future, but for now they are available
here for reference.


Get geographic metadata from CaltechDATA with WKT representations in a csv file. 
You can import this to a GIS program like QGIS
using a delimited text import and projection epsg:4326. You'll have to do one
import for Geometry type Point and another for Geometry type Polygon. 

```
python get_geo.py caltechdata_geo.csv
```

You can filter by keyword

```
python get_geo.py caltechdata_geo.csv -keywords TCCON
```


