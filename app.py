import requests
import json
import datetime
from flask import Flask, request
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



@app.route('/arrivals', methods=['POST'])
def get_next_arrival_time():
    

    json_dict = request.get_json(force=True)
    print json_dict


    action = json_dict['result']['parameters']['action']
    if action == "arrivals":

        marta_station = json_dict['result']['parameters']['marta_station']
        direction = json_dict['result']['parameters']['train_direction']
        line = json_dict['result']['parameters']['line']

        trains = _get_rail_info()
        necessary_fields = {}
        necessary_fields['STATION'] = marta_station

        arriving_trains = []

        if direction is not None  and direction != "":
            necessary_fields['DIRECTION'] = direction.upper()

        if line is not None  and line != "":
            necessary_fields['LINE'] = line.upper()

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
            response['speech'] = ""
            response['displayText'] = ""
            for train in arriving_trains:
                arrival_time = train['WAITING_TIME'].lower()

                if arrival_time == "arriving":
                    response['speech'] = response['speech'] + train['LINE'] + " line " + train['DIRECTION'] + "bound " + " Arriving station. "
                    response['displayText'] = response['speech'] + train['LINE'] + " line " + train['DIRECTION'] + "bound " + " Arriving station. "

                elif arrival_time == "boarding":
                    response['speech'] = response['speech'] + train['LINE'] + " line " + train['DIRECTION'] + "bound " + " Boarding. "
                    response['displayText'] = response['speech'] + train['LINE'] + " line " + train['DIRECTION'] + "bound " + " Boarding. "

                
                else:
                    response['speech'] = response['speech'] + train['LINE'] + " line " + train['DIRECTION'] + "bound " + " arriving station in " + train['WAITING_TIME'] + ". "
                    response['displayText'] = response['speech'] + train['LINE'] + " line " + train['DIRECTION'] + "bound " + " arriving station in " + train['WAITING_TIME'] + ". "




        response['speech'] = response['speech'].lower()
        response['displayText'] = response['displayText'].lower()

        response['speech'] = response['speech'].replace('sbound', 'southbound')
        response['speech'] = response['speech'].replace('nbound', 'northbound')
        response['speech'] = response['speech'].replace('wbound', 'westbound')
        response['speech'] = response['speech'].replace('ebound', 'eastbound')


        response['data'] = arriving_trains

        '''response = {}
        response['source'] = 'marta_api'
        response['speech'] = "The station you chose is " + marta_station + direction + line
        response['displayText'] = "The station you chose is " + marta_station + direction + line'''

        return json.dumps(response)

    elif action == "parking":
        marta_station = json_dict['result']['parameters']['marta_station']


        list_of_marta_stations_with_parking = ['MEDICAL CENTER STATION', 'DUNWOODY STATION', 'SANDY SPRINGS STATION', 'NORTH SPRINGS STATION', 'LINDBERGH STATION', 'LENOX STATION', 'INDIAN CREEK STATION']

        ##check if marta_station is null or empty "", then return message for all stations
        response = {}
        response['source'] = 'marta_api'
        response['speech'] = "shit to say"
        response['displayText'] = 'shit to print'

        if marta_station == "":
            string_of_all_stations = ', '.join(list_of_marta_stations_with_parking)
            response['speech'] = "Here are all the Marta Stations with parking " + string_of_all_stations
            response['displayText'] = "Here are all the Marta Stations with parking " + string_of_all_stations

        elif marta_station in list_of_marta_stations_with_parking:
            response['speech'] = marta_station + " has parking"
            response['displayText'] = marta_station + " has parking"

        else:
            response['speech'] = marta_station + " does not have parking"
            response['displayText'] = marta_station + " does not have parking"


        return json.dumps(response)



    elif action == "bathroom":
        marta_station = json_dict['result']['parameters']['marta_station']

        list_of_marta_stations_with_bathrooms = ["NORTH SPRINGS STATION", "DORAVILLE STATION", "LINDBERGH STATION", "ARTS CENTER STATION",'KENSINGTON STATION', "AVONDALE STATION", "INDIAN CREEK STATION", "FIVE POINTS STATION", "PEACHTREE CENTER STATION", "HAMILTON E HOLMES STATION", "WEST END STATION", "COLLEGE PARK STATION"]

        response = {}
        response['source'] = 'marta_api'
        response['speech'] = 'something'
        response['displayText'] = 'something'

        string_of_all_bathrooms = ', '.join(list_of_marta_stations_with_bathrooms)

        if marta_station == "":
            response['speech'] = "Here are all the stations with bathrooms " + string_of_all_bathrooms

        elif marta_station in list_of_marta_stations_with_bathrooms:
            response['speech'] = marta_station + " has a bathroom"

        else:
            response['speech'] = marta_station + "does not have a bathroom"

        return json.dumps(response)

    elif action == "amenities":
        map_of_marta_stations_by_amenitie = {
            'zip_car' : ['BROOKHAVEN STATION'],
            'bike_repair': ['KENSINGTON STATION','LENOX STATION'],
            'ride_store' : ['LENOX STATION']
        }
        amenity = json_dict['result']['parameters']['amenities']

        response = {}
        response['source'] = "marta_api"


        marta_station = json_dict['result']['parameters']['marta_station']
        if amenity not in map_of_marta_stations_by_amenitie:
            response['speech'] = "amenity not found"
            response['displayText'] = "amenity not found"
            return json.dumps(response)
            
        list_of_marta_stations_with_amenity = map_of_marta_stations_by_amenitie[amenity]

        if marta_station == "":
            
            string_of_all_stations = ', '.join(list_of_marta_stations_with_amenity)
            response['speech'] = "these are the marta stations with bike repairs centers " + string_of_all_stations
            response['displayText'] = "these are the marta stations with bike repair centers " + string_of_all_stations

        elif marta_station in list_of_marta_stations_with_amenity:
            response['speech'] = marta_station + "has this amenity"
            response['displayText'] = marta_station + "has this amenity"

        else:
            response['speech'] = marta_station + " does not have this amenity"
            response['displayText'] = marta_station + "has this amenity"

        return json.dumps(response)

    elif action == "bus_routes":
        map_of_bus_routes_by_marta_stations = {

    "ARTS CENTER STATION": ['Route 37 Atlantic Station' , 'Route 110 The Peach'],



    'BUCKHEAD STATION': ['Route 110 The Peach'],



    'MIDTOWN STATION': ['Route 12 Cumberland', 'Route 27 Ansley Mall', 'Route 36 Virginia Highland', 'Route 109 Boulevard'],



    "FIVE POINTS STATION": ['Route 3 Martin Luther King', 'Route 13 Hunter Hills', 'Route 16 North Highland', 'Route 32 Bouldercrest', 'Route 42 Pryor Rd', 'Route 49 McDonough Blvd', 'Route 51 Joseph E Boone Blvd', '55 Jonesboro Rd/Hutchens Rd/Forest Pkwy'],



    'WEST END STATION': ['Route 67 Dixie Hills', 'route 68 Donnelly', 'Route 71 Cascade', 'route 81 Adams Park', 'Route 94 Northside Dr', 'route 95 Hapeville']


    }
        marta_station = json_dict['result']['parameters']['marta_station']

        response = {}
        response['source'] = "marta_api"

        if marta_station == "":

            stations_string_list = ", ".join(map_of_bus_routes_by_marta_stations.keys())
            response['speech'] = "supported stations are " + stations_string_list
            response['displayText'] = "supported stations are " + stations_string_list


        if marta_station not in map_of_bus_routes_by_marta_stations.keys():
            response['speech'] = "Sorry this " + marta_station  + " is currently not supported"
            response['displayText'] = "Sorry this " + marta_station  + " is currently not supported"
        
        else:
            routes_string = ', '.join( map_of_bus_routes_by_marta_stations[marta_station] )

            response['speech'] = "Routes for " + marta_station + " " + routes_string
            response['displayText'] = "Routes for " + marta_station + " " + routes_string

        return json.dumps(response)



        

#print get_next_arrival_time('BROOKHAVEN STATION')

'''if __name__ == "__main__":  
    app.run()'''
