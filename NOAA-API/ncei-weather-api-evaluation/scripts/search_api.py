"""search_api module"""
import json
import math
import time
import logging
import argparse
import copy
import sys
import re
import os
import requests

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


# given test query parameters
parser = argparse.ArgumentParser(
    description='Query the NCEI API with given arguments.')

group1 = parser.add_argument_group('Required', 'Required arguments')
group1.add_argument('-d', '--dataset', type=str, required=True,
                    help='Dataset to search through.  Found in NCEI documentation or site.')
group1.add_argument('-la', '--latitude', type=float, required=True,
                    help='Latitude of the source point')

group1.add_argument('-lo', '--longitude', type=float, required=True,
                    help='Longitude of the source point')

group1.add_argument('-sd', '--startdate', type=str, required=True,
                    help='startDate in YYYY-MM-DD format')

group1.add_argument('-ed', '--enddate', type=str, required=True,
                    help="endDate in YYYY-MM-DD format")

group1.add_argument('-a', '--attributes', type=str, required=True,
                    help='List of data types from NCEI.  1 minimum required',
                    nargs='+')

group2 = parser.add_argument_group('Optional', 'Optional arguments')
HELP_STRING = "maximum length of the boundingbox in km.  defaults to 100."
group2.add_argument('-b', '--bboxsize', type=float,
                    help=HELP_STRING, default=100)

group2.add_argument('-s', '--stationspath', type=str,
                    default="data/stations_sorted.json",
                    help='sorted stations path.  default: "data/stations_sorted.json"')

group2.add_argument('-dp', '--datapath', type=str,
                    default="data/stations/",
                    help='path for the actual data.  default: "data/stations/"')

group2.add_argument('-dmp', '--dumpraw', action='store_true',
                    default=False,
                    help='Dump the raw search and error results and to the dump path under name search.json/error.json respectively')

group2.add_argument('-dmppath', '--dumppath', type=str,
                    default="data/raw/",
                    help='path for the raw search data.  default: "data/raw/"')

group2.add_argument('-i', '--includeincomplete', action='store_true',
                    help='Store stations with attributes present, but for dates outside the request')
group2.add_argument('-na', '--noattributes',  action='store_true',
                    help="when set it will search for attributes and will return the first applicable station.  Useful for finding attributes in a dataset.")

args = parser.parse_args()

LATITUDE = args.latitude
LONGITUDE = args.longitude
SORTEDSTATIONSFILEPATH = args.stationspath
BBOXSIZE = args.bboxsize
ATTRIBUTES = args.attributes
STARTDATE = args.startdate
ENDDATE = args.enddate
DATAFILEPATH = args.datapath
DUMPRAW = args.dumpraw
DUMPPATH = args.dumppath
DATASET = args.dataset
SAVEPARTIAL = args.includeincomplete
NOATTRIBUTES = args.noattributes

RADIUS = 6371.0
RADLATITUDE = math.radians(float(LATITUDE))
RADLONGITUDE = math.radians(float(LONGITUDE))

# Calculating the size of the bounding box based on length
# returns a string in the correct format for the API request
def calculate_bbox(length):
    """calculate the bbox and return it"""
    box_lat_len = length * (360 / 40075)
    # long is depended on lat
    box_long_len = length * (360 / (math.cos(RADLATITUDE) * 40075))

    # upper left coordinates of the box
    upper_left = str(box_lat_len + LATITUDE) + ', ' + \
        str(-box_long_len + LONGITUDE)

    # lower right coordinates of the box
    lower_right = str(LATITUDE - box_lat_len) + ', ' + \
        str(LONGITUDE + box_long_len)

    # combine into a format acceptable for an API request
    bbox = upper_left + ', ' + lower_right

    return bbox

# Set the parameters and iterate through increasing the bbox length
# until the desired station(s) are returned
def find_station(length):
    """find stations from API function """
    station_found = False
    while station_found is False:
        bbox = calculate_bbox(length)

    # given test query parameters
        parameters = {'dataset': DATASET,
                      'bbox': bbox,
                      'startDate': STARTDATE, 'endDate': ENDDATE,
                      # 'text': DATASET,
                      # 'limit': '10',
                      # 'offset': '0',
                      # 'available': 'true'
                      }

    # request with parameters

        # trying not to get blacklisted

        # Print the request to be sent
        logging.info('Requesting data for:')
        logging.info('		Dataset : %s', DATASET)
        logging.info('		Date Range : %s - %s', STARTDATE, ENDDATE)
        logging.info('      %f sqkm box at coordinates : %s', length**2, bbox)

        time.sleep(0.10)
        response = requests.get(
            "https://www.ncei.noaa.gov/access/services/search/v1/data",
            parameters)

        # try request necessary for Exception thrown when there is no station
        stations = []
        station_data = {"stations": [], "metadata": {}}
        station_data["metadata"]["command"] = (' '.join(sys.argv[0:]))
        attributes = []
        try:
            # results is a list of stations

            for station in response.json()["results"]:
                short_station = station['stations'][0]

                # track the stations for passing to other scripts later
                stations.append(short_station['id'])

                # clear attributes from prev station
                attributes.clear()
                for attribute in short_station['dataTypes']:
                    attributes.append(
                        {'id': attribute['id'],
                         'dateRange': attribute['dateRange']})

                # Add the station entry to the final list
                latitude = station['location']['coordinates'][1]
                longitude = station['location']['coordinates'][0]
                station_data["stations"].append(
                    {"station": short_station['id'],
                     "dataTypes": copy.deepcopy(attributes),
                     'latitude': latitude,
                     'longitude': longitude
                     })

        # Process no stations present Exception
        except KeyError:
            if DUMPRAW is True:
                if not os.path.exists(DUMPPATH):
                    os.makedirs(DUMPPATH)
                with open(DUMPPATH + "error.json", 'w') as fout:
                    print(json.dumps(response.json(), indent=2), file=fout)
            try:
                if(response.json()["errorCode"] == 400 |
                        response.json()["errorCode"] == 500):
                    logging.error(
                        "Check your dataset if it appears to be timing out")

                    logging.error(
                        'Status Code %i Recieved', response.status_code)
                    logging.error("		%s", response.json()['errorMessage'])
                    for error in response.json()['errors']:
                        logging.error("		%s", error['message'])
                    sys.exit()
            except KeyError:
                logging.info("No stations present in current search.")

        # Exit as soon as 1 or more stations are present in the Bounding box
        # here would be a good place to scan through the station list for
        # required attributes if we need certain ones.
        if len(stations) > 0:
            station_found = True
            if DUMPRAW is True:
                if not os.path.exists(DUMPPATH):
                    os.makedirs(DUMPPATH)
                with open(DUMPPATH + "search.json", 'w') as fout:
                    print(json.dumps(response.json(), indent=2), file=fout)
            return station_data

        # double the size of the box leßngth if nothing is present
        length *= 2

        # Exceeded set boundingbox size
        if length > BBOXSIZE:
            logging.warning("Search exceeded maximum box length.")
            logging.warning("Adjust search criteria.")
            sys.exit()


STARTING_LEN = 1
station_data_raw = find_station(STARTING_LEN)


def sort_function(given_station):  # Function for sorting the entries by distance
    """sorting function"""
    return given_station["distance"]

# Scan the stations for necessary attributes in the correct date range
def check_attributes(given_data, given_dict):
    """check attributes of current dataset"""
    returning_stations = {"stations": []}
    returning_stations["metadata"] = copy.deepcopy(given_data["metadata"])
    for station in given_data["stations"]:
        for data_type in station["dataTypes"]:
            if data_type['id'] in given_dict:
                # regex the date format
                start_string = data_type["dateRange"]["start"]
                end_string = data_type["dateRange"]["end"]
                pattern = '(.*)T'
                start_result = re.match(pattern, start_string)
                end_result = re.match(pattern, end_string)

                # check the dates
                if (time.strptime(start_result.group(1), "%Y-%m-%d") <= time.strptime(STARTDATE, "%Y-%m-%d")) & \
                        (time.strptime(end_result.group(1), "%Y-%m-%d") >= time.strptime(ENDDATE, "%Y-%m-%d")):
                    # Valid for the range
                    given_dict[data_type['id']] = True
                    if station not in returning_stations["stations"]:
                        returning_stations["stations"].append(station)
                else: # if not valid print a warning
                    logging.warning("dataType %s is present only for date range %s - %s for station %s",
                                    data_type['id'], start_result.group(1), end_result.group(1), station["station"])
                    if SAVEPARTIAL is True: # save if -i flag is asserted
                        logging.warning(
                            "-i flag asserted, station %s data saved!", station['station'])
                        given_dict[data_type['id']] = True
                        if station not in returning_stations["stations"]:
                            returning_stations["stations"].append(station)
    return returning_stations

# if searching for certain attributes check current stations and then
# re-iterate through the find_station function until either the bbox limit
# is reached or you find at least 1 station with the right attribute and dates
if NOATTRIBUTES is False:
    # Create a dictionary for marking discovered attributes
    attributeSetDefaults = [False] * len(ATTRIBUTES)
    attribute_dict = dict(zip(ATTRIBUTES, attributeSetDefaults))

    # Check the first return of data for the correct attributes
    returned_stations = check_attributes(station_data_raw, attribute_dict)

    # Scan the marked up dictionary tracking the attributes that aren't gathered
    LOOKUP_VALUE = False
    falseEntries = []
    for key, value in attribute_dict.items():
        if value == LOOKUP_VALUE:
            falseEntries.append(key)

    # if we have not exceeded the bbox and are missing attributes extend the base search
    while (STARTING_LEN * 2 <= BBOXSIZE) & (len(falseEntries) > 0):
        STARTING_LEN = STARTING_LEN * 2

        logging.info(
            "expanding search for Attributes %s with length %i", ','.join(ATTRIBUTES), STARTING_LEN)

        # rerun the search and attribute marking
        station_dataRaw = find_station(STARTING_LEN)
        returned_stations = check_attributes(station_dataRaw, attribute_dict)

        # Rescan the attribute Dictionary
        falseEntries.clear()
        for key, value in attribute_dict.items():
            if value == LOOKUP_VALUE:
                falseEntries.append(key)

    # All attributes have been found
    if len(falseEntries) == 0:
        logging.info("All attributes are included!")
    else:  # not all attributes were found, and met edge of bbox
        logging.info(
            "Attributes: %s are not found in given bounding box!", ','.join(falseEntries))
else:
    # return the base data if no attributes are requested
    returned_stations = station_data_raw


# calculate distance from the given point for every station
def distance_calc(given_stations):
    """calculate distance for each station present"""
    for entry in given_stations:
        # Calculate the distance in km from the point

        station_latitude = math.radians(float(entry['latitude']))
        station_longitude = math.radians(float(entry['longitude']))

        distance_lat = RADLATITUDE - station_latitude
        distance_long = RADLONGITUDE - station_longitude
        calc1 = math.sin(distance_lat / 2)**2 + math.cos(station_latitude) * \
            math.cos(RADLATITUDE) * math.sin(distance_long / 2)**2
        calc2 = 2 * math.atan2(math.sqrt(calc1), math.sqrt(1 - calc1))
        distance = RADIUS * calc2

        entry.update({'distance': distance})

    return given_stations


returned_stations["stations"] = distance_calc(returned_stations["stations"])
# Run the distance sort
returned_stations["stations"] = sorted(
    returned_stations["stations"], key=sort_function)

stationNum = len(returned_stations["stations"])

logging.info("returning %i station(s) in %s",
             stationNum, SORTEDSTATIONSFILEPATH)

# print the sorted and useful list
with open(SORTEDSTATIONSFILEPATH, 'w') as sortedout:
    print(json.dumps(returned_stations, indent=2), file=sortedout)

# call other API for actual data for all of the stations, each individually named

for station in returned_stations["stations"]:

    data_parameters = {
        'dataset': DATASET,
        'startDate': STARTDATE, 'endDate': ENDDATE,
        'stations': station['station'],
        'format': 'json'
    }

    response = requests.get(
        "https://www.ncei.noaa.gov/access/services/data/v1", data_parameters)

    if not os.path.exists(DATAFILEPATH):
        os.makedirs(DATAFILEPATH)
    save_path = DATAFILEPATH + station['station'] + '.json'
    with open(save_path, 'w') as file_out:
        print(json.dumps(response.json(), indent=2), file=file_out)
