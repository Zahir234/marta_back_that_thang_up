# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]

from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

import logging

import json
import datetime
from flask import Flask, request, abort, make_response
from flask_cors import CORS

import datastore_manager
import shortuuid

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore

from werkzeug.http import parse_options_header

app = Flask(__name__)
app.debug = True
CORS(app)

ALPHABET_FOR_SECRETS = "0123456789ABCDEF"
secret_generator = shortuuid.ShortUUID(alphabet=ALPHABET_FOR_SECRETS)

clientId = '692772929154-2nasht9k1q88nm15mekm0s6evt1pjin2.apps.googleusercontent.com'
client_secret = 'ayrXnhy-BmSXafYo-5Iei93I'

project = "demolisherapp"
kind = 'exams'
dm = datastore_manager.DatastoreManager(project, kind, lcp='QA')
blob_kind = 'blobs'
dm_for_blobs = datastore_manager.DatastoreManager(project, blob_kind, lcp='QA')


EXAM_PROJECTION = ['file', 'school', 'school_class', 'description', 'professor', 'free_or_nah', 'price', 'number_of_downloads', 'tags']


def exam_secret_generator():
    secret = secret_generator.random(length=16)
    #secret = shortuuid.ShortUUID().random(length=22)
    return secret


####Exams only stuff
@app.route('/exam/<exam_id>', methods=['GET'])
def get_exam(exam_id):
    if exam_id is None or exam_id == "":
           abort(400, '''missing exam_id''')

    print exam_id
    
    json_dict = dm.get_entity(int(exam_id))

    json_dict.pop('secret', None)
    json_dict['id'] = str(json_dict.key.id_or_name)

    return json.dumps(json_dict)

@app.route('/exam/<exam_id>/secret/<secret>', methods=['GET'])
def get_exam_with_secret(exam_id, secret):
    if exam_id is None or exam_id == "" or secret is None or secret == "":
        abort(400, '''missing exam_id or secret''')
    
    json_dict = dm.get_entity(int(exam_id))

    secret = secret.replace('-', '')
    if json_dict['secret'] == secret:
        json_dict['id'] = str(json_dict.key.id_or_name)
        json_dict['secret'] = '-'.join([json_dict['secret'][i:i+4] for i in range(0, len(json_dict['secret']), 4)])
        return json.dumps(json_dict)
    else:
        abort(400, '''incorrect secret ''')

'''{file: "", school: "" , 'school_class : "", secret : "", description : "", professor : "", free_or_nah : False, number_of_downloads : "", tags : [] }'''
@app.route('/exam', methods=['POST'])
def create_exam():
    secret = exam_secret_generator()

    json_dict = request.get_json(force=True)

    json_dict['secret'] = secret


    list_of_neccessary_fields = ['file', 'school', 'school_class', 'secret', 'description', 'professor', 'free_or_nah']

    list_of_optional_stuff = ['number_of_downloads', 'tags']

    if not dm_for_blobs.get_entity(json_dict['file']):
        abort(400, "Missing files")

    if not json_dict['free_or_nah']:
        json_dict['wallet'] = exam_secret_generator()
        list_of_neccessary_fields.append('price')

    for item in list_of_neccessary_fields:
        if not item in json_dict or json_dict[item] == None or json_dict[item] == "":
            abort(400, '''{missing_field} missing field or malformed'''.format(missing_field=item))

    for item in list_of_optional_stuff:
        if not item in json_dict or json_dict[item] == None:
            if item  == 'number_of_downloads':
                json_dict[item] = 0

            elif item == 'tags':
                json_dict[item] = []

    key = dm.add_entity(json_dict)

    json_dict['id'] = str(key.id)
    json_dict['secret'] = '-'.join([json_dict['secret'][i:i+4] for i in range(0, len(json_dict['secret']), 4)])
    return json.dumps(json_dict)


@app.route('/exam/<exam_id>/secret/<secret>', methods=['DELETE'])
def delete_exam(exam_id, secret):

    if exam_id is None or exam_id == "" or secret is None or secret == "":
        abort(400, '''missing exam_id''')

    json_dict = dm.get_entity(exam_id)

    if json_dict['secret'] == secret:
        result = dm.delete_entity(exam_id)
        return json.dumps(result)

    else:
        abort(400, '''incorrect secret ''')


##Bitcoin stuff
## wallet creation
## process payment


###Exam pdf manager
# get pdf
# add file and return file id
# delete file with file id
@app.route('/generate_blobstore_url')
def blobstore_url_gen():
    upload_url = blobstore.create_upload_url('/upload_blob')
    html_for_testing = """
<html><body>
<form action="{0}" method="POST" enctype="multipart/form-data">
  Upload File: <input type="file" name="file"><br>
  <input type="submit" name="submit" value="Submit">
</form>
</body></html>""".format(upload_url)
    return upload_url


@app.route('/upload_blob', methods=['GET', 'POST'])
def post_new_blob():
    print "######################################"
    print request.method
    print "HEYYyyyyyyyyyyyyYYYYYYYYYYY"
    f = request.files['file']
    header = f.headers['Content-Type']
    print "??????????????????????? this the header"
    print header
    parsed_header = parse_options_header(header)
    blob_key = parsed_header[1]['blob-key']
    creation_time = datetime.datetime.utcnow()

    print blob_key

    json_dict = {}
    json_dict['creation_time'] = creation_time
    json_dict['id'] = blob_key

    key = dm_for_blobs.add_entity_with_id(json_dict)

    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    print key
    resp = {'blob_key': str(key.id_or_name)}

    return json.dumps(resp)

@app.route('/blob/<blob_id>', methods=['GET'])
def get_blob(blob_id):
    blob = blobstore.get(blob_id)
    resp = make_response(blob.open().read())
    resp.headers['Content-Type'] = blob.content_type
    return resp


@app.route('/blob/<blob_id>', methods=['DELETE'])
def delete_blob(blob_id):
    blobstore.delete(blob_id)
    dm_for_blobs.delete_entity(blob_id)
    return "OK"

@app.route('/frontend/get_schools', methods=['GET'])
def get_list_of_all_schools():
    gql_query = "SELECT DISTINCT school from {kind}".format(kind=kind)
    query = dm.client.query(kind=kind, projection=['school'], distinct_on=['school'])
    results = dm.run_query(query)

    response = []
    for entity in results:
        school = {}
        school['value'] = entity['school'].lower()
        school['display'] = entity['school']

        response.append(school)

    return json.dumps(response)

@app.route('/frontend/school/<school>/get_classes', methods=['GET'])
def get_list_of_all_classes(school):
    print school
    query = dm.client.query(kind=kind, projection=['school_class'], distinct_on=['school_class'])
    query.add_filter('school', '=', school)
    results = dm.run_query(query)

    response = []
    for entity in results:
        school_class = {}
        school_class['value'] = entity['school_class'].lower()
        school_class['display'] = entity['school_class']

        response.append(school_class)


    return json.dumps(response)

@app.route('/frontend/school/<school>/school_class/<school_class>/get_resources', methods=['GET'])
def get_list_of_resources(school, school_class):
    query = dm.client.query(kind=kind)
    query.add_filter('school', '=', school)
    query.add_filter('school_class', '=', school_class)

    results = dm.run_query(query)

    for entity in results:
        print entity
        entity['id'] = str(entity.key.id_or_name)
        entity.pop('secret', None)



    return json.dumps(results)




###Create views for all schools, all classes in a schoool, and all exams in a school and school_class

'''if __name__ == "__main__":  
    app.run()'''

    



