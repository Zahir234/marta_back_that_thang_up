import requests
import json
import datetime
from flask import Flask
from dateutil import parser


MARTA_API_KEY = "4edfdeb5-4f20-4139-9997-3568a2c88c80"

rail_url = "http://developer.itsmarta.com/RealtimeTrain/RestServiceNextTrain/GetRealtimeArrivals"


app = Flask(__name__)
app.debug = True

def _get_rail_info():
    info = requests.get(rail_url, params={'apiKey': MARTA_API_KEY})
    return info.json()


def _get_destinations_by_train_map():
    destinations_by_train_map = {}

    marta_info = _get_rail_info()

    for train in marta_info:
        if train['TRAIN_ID'] in destinations_by_train_map:
            destinations_by_train_map[ train['TRAIN_ID'] ].append(train)
        else:
            destinations_by_train_map[ train['TRAIN_ID'] ] = [ train ]

    return destinations_by_train_map




@app.route('/arrivals/marta_station/<marta_station>', methods=['POST', 'GET'])
def get_next_arrival_time(marta_station):
    direction=None
    line=None
    trains = _get_rail_info()
    necessary_fields = {}
    necessary_fields['STATION'] = marta_station

    arriving_trains = []

    if direction is not None  and direction != "":
        necessary_fields['DIRECTION'] = direction.upper()

    if line is not None  and line != "":
        list_of_neccessary_fields['LINE'] = line.upper()

    for train in trains:
        all_fields_match = True
        for key in necessary_fields:
            if necessary_fields[key] != train[key]:
                all_fields_match = False
                break

        if all_fields_match:
            arriving_trains.append(train)


    response = {}
    response['source'] = 'marta_api'

    if len(arriving_trains) == 0:
        response['speech'] = "No results"
        response['displayText'] = "No results"


    else:
        arrival_time = arriving_trains[0]['WAITING_TIME'].lower()
        if arrival_time == "arriving":
            response['speech'] = "Arriving"
            response['displayText'] = "Arriving"

        elif arrival_time == "boarding":
            if len(arriving_trains) > 1:
                response['speech'] = "Boarding, but next comes at " + arriving_trains[1]['WAITING_TIME']
                response['displayText'] = "Boarding, but next comes at " + arriving_trains[1]['WAITING_TIME']

            else:
                response['speech'] = "Boarding"
                response['displayText'] = "Boarding"

        
        else:
            response['speech'] = "arriving in " + arriving_trains[0]['WAITING_TIME']
            response['displayText'] = "arriving in " + arriving_trains[0]['WAITING_TIME']
    
    return json.dumps(response)

#print get_next_arrival_time('BROOKHAVEN STATION')

if __name__ == "__main__":  
    app.run()
