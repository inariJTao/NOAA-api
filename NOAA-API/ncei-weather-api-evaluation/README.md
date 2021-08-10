# Overview
Python-based scripts for pulling NCEI weather data through their API's based on requested coordinates, dataset, bounding box, date range, and attributes.  

a list of stations can be found in the generalNotes file in the documents folder, along with other useful documents
## Confluence
https://inariag.atlassian.net/wiki/spaces/CCD/pages/1759313921/NCEI+Data+API+User+Guide

# Building the container

## Using make

   	make build

## OR Using the command

   	docker rm foo ; docker rmi ncei-weather-img; docker build -t ncei-weather-img .

# Running the Image

## Using make

   	make run

## OR Using the Command

   	docker run -it -v $PWD/data:/app/scripts/data --name="foo" ncei-weather-img /bin/bash

## Other make commands

   	make full - runs build followed by run
	
   	make clean - cleans the working directory and docker image/container

# Running the scripts in the container

- will tell you necessary and optional arguments

		python3 get_data.py -h

      python3 search_api.py -h

# Script specific information

## get_data.py
### Overview
will return a json file with the requested information

### Help Argument
  - -h, --help            show this help message and exit

### Required Arguments

  - -d DATASET, --dataset DATASET
                        The dataset to query
  - -sd STARTDATE, --startDate STARTDATE
                        The starting date of the requested data
  - -ed ENDDATE, --endDate ENDDATE
                        The ending date of the requested data
  - -s StationID [StationID ...], --stations StationID [StationID ...]
                        Station ID

### Optional arguments

  - -dt DATATYPES [DATATYPES ...], --dataTypes DATATYPES [DATATYPES ...]
                        List of dataTypes. Defaults to all dataTypes
  - -bb N W S E, --bbox N W S E
                        4 Coords of the Bounding Box ordered N, W, S, E
  - -nl, --noloc          Do not get coordinates and elevation of stations
                        in queried data.
  - -a, --attributes      Store attibutes of dataTypes
  - -o OUTPUT, --output OUTPUT
                        Set output path (default: data/dataOut.json

## search_api.py
### Overview
takes a dataset, long, lat, dateRange, and minimum of 1 attribute and returns a sorted list of the stations and the actual data of the stations in a seperate directory.  has several command line arguments listed below

### Arguments

### Help Argument
-  -h, --help            show this help message and exit

### Required Arguments

 - -d DATASET, --dataset DATASET
                        Dataset to search through. Found in NCEI
                        documentation or site.
 - -la LATITUDE, --latitude LATITUDE
                        Latitude of the source point
 - -lo LONGITUDE, --longitude LONGITUDE
                        Longitude of the source point
 - -sd STARTDATE, --startdate STARTDATE
                        startDate in YYYY-MM-DD format
 - -ed ENDDATE, --enddate ENDDATE
                        endDate in YYYY-MM-DD format
 - -a ATTRIBUTES [ATTRIBUTES ...], --attributes ATTRIBUTES [ATTRIBUTES ...]
                        List of attributes from NCEI. 1 minimum required

### Optional Arguments

 - -b BBOXSIZE, --bboxsize BBOXSIZE
                        maximum length of the boundingbox in km.
                        defaults to 100.
 - -s STATIONSPATH, --stationspath STATIONSPATH
                        sorted stations path. default:
                        "data/stations_sorted.json"
 - -dp DATAPATH, --datapath DATAPATH
                        path for the actual data. default:
                        "data/stations/"
 - -dmp, --dumpraw       Dump the raw search and error results and to the
                        dump path under name search.json/error.json
                        respectively
 - -dmppath DUMPPATH, --dumppath DUMPPATH
                        path for the raw search data. default:
                        "data/raw/"
 - -i, --includeincomplete
                        Store stations with attributes present, but for
                        dates outside the request
 - -na, --noattributes   when set it will search for attributes
                        and will return the first applicable station.
                        Useful for finding attributes in a dataset.

# Example code executions
Example executions can be found on the confluence page:
https://inariag.atlassian.net/wiki/spaces/CCD/pages/1759313921/NCEI+Data+API+User+Guide


