import requests
import json
import datetime
#from flask import Flask
from dateutil import parser


MARTA_API_KEY = "4edfdeb5-4f20-4139-9997-3568a2c88c80"

rail_url = "http://developer.itsmarta.com/RealtimeTrain/RestServiceNextTrain/GetRealtimeArrivals"


#app = Flask(__name__)


def _get_rail_info():
	info = requests.get(rail_url, params={'apiKey': MARTA_API_KEY})
	return info.json()

def _create_trains_by_stations_and_directions_map():

	trains_by_stations_and_directions_map = {}


	trains = _get_rail_info()
	for train in trains:
		if (train['STATION'], train['DIRECTION']) in trains_by_stations_and_directions_map:
			trains_by_stations_and_directions_map[(train['STATION'], train['DIRECTION'])].append(train)

		else:
			trains_by_stations_and_directions_map[(train['STATION'], train['DIRECTION'])] = [train]

	return trains_by_stations_and_directions_map


def _get_destinations_by_train_map():
	destinations_by_train_map = {}

	marta_info = _get_rail_info()

	for train in marta_info:
		if train['TRAIN_ID'] in destinations_by_train_map:
			destinations_by_train_map[ train['TRAIN_ID'] ].append(train)
		else:
			destinations_by_train_map[ train['TRAIN_ID'] ] = [ train ]

	return destinations_by_train_map

def _get_next_destination(train_id):
	all_destiantions_ordered_by_train_id = _get_destinations_by_train_map()
	list_of_destinations = all_destiantions_ordered_by_train_id[ train_id ]

	neartest_destiantions_list = sorted(list_of_destinations, key=lambda k: parser.parse(k['NEXT_ARR']) )

	return neartest_destiantions_list

#@app.route('/station/<station>/direction/<direction>')
def get_trains_with_station_and_direction(station, direction):
	trains_by_stations_and_directions  = _create_trains_by_stations_and_directions_map()



	return json.dumps(trains_by_stations_and_directions[(station, direction)])

#@app.route('/train/<train_id>')
def get_next_destiantion(train_id):
	next_destination = _get_next_destination(train_id)
	return json.dumps(next_destination)

#print _get_rail_info()

print get_next_destiantion('104206')

