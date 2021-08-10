"""get_data module requests data with certain parameters from NCEI api"""
import json
import argparse
import logging
import requests

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


# given test query parameters
parser = argparse.ArgumentParser(
    description='Query the NCEI API with given arguments.')

group1 = parser.add_argument_group('Required', 'Required arguments')
group1.add_argument('-d', '--dataset', type=str, required=True,
                    help='The dataset to query')

group1.add_argument('-sd', '--startDate', type=str, required=True,
                    help='The starting date of the requested data')

group1.add_argument('-ed', '--endDate', type=str, required=True,
                    help='The ending date of the requested data')

group1.add_argument('-s', '--stations', metavar='StationID', type=str,
                    nargs='+', help='Station ID', required=True)
group2 = parser.add_argument_group('Optional', 'Required arguments')
group2.add_argument('-dt', '--dataTypes', type=str,
                    help='List of dataTypes.  Defaults to all dataTypes',
                    nargs='+')

group2.add_argument('-bb', '--bbox', type=str, nargs=4,
                    help='4 Coords of the Bounding Box ordered N, W, S, E',
                    metavar=('N', 'W', 'S', 'E'))

group2.add_argument(
    '-nl', '--noloc', action='store_true',
    help='Do not get coordinates and elevation of stations in queried data.')

group2.add_argument('-a', '--attributes', action='store_true',
                    help='Store attibutes of dataTypes')

group2.add_argument('-o', '--output', type=str, default='data/dataOut.json',
                    help='Set output path (default: data/dataOut.json')
args = parser.parse_args()

DATASET = args.dataset
STARTDATE = args.startDate
ENDDATE = args.endDate
STATIONLIST = args.stations
DATATYPES = args.dataTypes
BBOX = args.bbox
NOLOC = args.noloc
ATTRIBUTES = args.attributes
OUTPUTFILE = args.output

# Station list so they can be easily modified as needed
# concatenate into a string
STATIONSTRING = ','.join(STATIONLIST)


# parameters for the API request
parameters = {
    'dataset': DATASET,
    'startDate': STARTDATE, 'endDate': ENDDATE,
    'stations': STATIONSTRING,
    'format': 'json'
}

if DATATYPES is not None:
    DATATYPESSTRING = ','.join(DATATYPES)
    parameters['dataTypes'] = DATATYPESSTRING
if BBOX is not None:
    BBOXSTRING = ','.join(BBOX)
    parameters['boundingbox'] = BBOXSTRING
if NOLOC is not True:
    parameters['includeStationLocation'] = '1'
if ATTRIBUTES is True:
    parameters['includeAttributes'] = '1'

# Print the request to be sent
logging.info('Requesting data for:')
logging.info('		Stations : %s', STATIONSTRING)
logging.info('		Dataset : %s', DATASET)
logging.info('		Date Range : %s - %s', STARTDATE, ENDDATE)
if DATATYPES is not None:
    logging.info('     DataTypes : %s', DATATYPESSTRING)
if BBOX is not None:
    logging.info('     Bounding Box : %s', BBOXSTRING)


# request with parameters
response = requests.get(
    "https://www.ncei.noaa.gov/access/services/data/v1", parameters)


# print queried data to file
with open(OUTPUTFILE, 'w+') as fout:
    print(json.dumps(response.json(), indent=2), file=fout)


# Process either a valid recieve or an error
if response.status_code == int('200'):
    logging.info('Data Recieved Successfully at %s!', OUTPUTFILE)
else:  # ERROR recieved, print useful information to terminal
    logging.error('Status Code %i Recieved', response.status_code)
    logging.error('     %s', response.json()["errorMessage"])
    for error in response.json()['errors']:
        logging.error('		%s', error["message"])
