exams_json = '''[ {
    "school": "Georgia State University",
    "class": "PHYS1001",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
},
{
    "school": "Georgia State University",
    "class": "PHYS1002",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : false,
    "price" : "4.50"
},
{
    "school": "Georgia State University",
    "class": "PHYS1003",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : false,
    "price" : "4.50"
},
{
    "school": "Georgia State University",
    "class": "BIO1001",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : false,
    "price" : "3.50"
},
{
    "school": "Georgia State University",
    "class": "BIO1002",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : false,
    "price" : "3.50"
},
{
    "school": "Georgia State University",
    "class": "BIO1003",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : false,
    "price" : "4.50"
},
{
    "school": "Colorado State University",
    "class": "CSC1001",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
},
{
    "school": "Colorado State University",
    "class": "CSC1002",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
},
{
    "school": "Colorado State University",
    "class": "CSC1003",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
},
{
    "school": "University of Georgia",
    "class": "PHYS1001",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
},
{
    "school": "University of Georgia",
    "class": "PHYS1002",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
},
{
    "school": "University of Georgia",
    "class": "PHYS1003",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
},
{
    "school": "Georgia Southern University",
    "class": "CSC1001",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
},
{
    "school": "Georgia Southern University",
    "class": "CSC1002",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
},
{
    "school": "Georgia Southern University",
    "class": "CSC1003",
    "secret": "1234",
    "file": "file_key1",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
} ]'''


import json
import requests
import unittest
import shutil
import filecmp

insert_exam = '{base_address}/exam'


def upload_blob():
    files = {'file': open('pic.jpg', 'rb')}

    base_address = 'http://127.0.0.1:8080'
    get_blob_upload_url = '{base_address}/generate_blobstore_url'

    resp = requests.get(get_blob_upload_url.format(base_address=base_address))

    upload_url = resp.text



    print "********************************"
    print upload_url

    resp = requests.post(upload_url, files=files)

    response_json = resp.json()

    return response_json['blob_key']

def insert_all_entities(lcp, entities):
    blob_key = upload_blob()
    base_address = ""
    if lcp.upper() == "DEV":
        base_address = 'http://127.0.0.1:8080'

    for exam in entities:
        exam['file'] = blob_key
        url = insert_exam.format(base_address=base_address)
        resp = requests.post(url, data=json.dumps(exam))

    if not resp.status_code ==  requests.codes.ok:
        print "yooo something is broken"

exams = json.loads(exams_json)

insert_all_entities('dev', exams)

class SchoolAndClassViewsTests(unittest.TestCase):

    def test_school(self):

        get_school_view_url = '{base_address}/frontend/get_schools'

        test_case_json = '''["Colorado State University", "Georgia Southern University", "Georgia State University", "University of Georgia"]'''

        test_case_list = json.loads(test_case_json)

        base_address = 'http://127.0.0.1:8080'
        url = get_school_view_url.format(base_address=base_address)
        school_view_response = requests.get(url)

        response_json= school_view_response.json()

        all_schools_in_db = []
        for entity in response_json:
            all_schools_in_db.append(entity['school'])

        self.assertTrue(set(test_case_list).issubset(set(all_schools_in_db)))


    def test_classes(self):
        clases_related_to_gsu_json = ''' ["BIO1001", "BIO1002", "BIO1003", "PHYS1001", "PHYS1002", "PHYS1003" ]'''

        test_case_list = json.loads(clases_related_to_gsu_json)


        get_class_view_url = '{base_address}/frontend/school/{school}/get_classes'

        school = "Georgia State University"

        base_address = 'http://127.0.0.1:8080'
        class_view_url = get_class_view_url.format(base_address=base_address, school=school)

        response = requests.get(class_view_url)
        response_json = response.json()

        all_classes_in_db = []
        for entity in response_json:
            all_classes_in_db.append(entity['class'])

        self.assertTrue(set(test_case_list).issubset(set(all_classes_in_db)))



class ExamTests(unittest.TestCase):
    def test_free_exam_addition(self):
        json_test_string = '''{{
    "school": "Georgia Southern University",
    "class": "CSC1001",
    "file": "{blob_key}",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : true
}}'''.format(blob_key=upload_blob())

        json_test_dict = json.loads(json_test_string)
        create_exam_url = '{base_address}/exam'
        base_address = 'http://127.0.0.1:8080'
        url = create_exam_url.format(base_address=base_address)
        resp = requests.post(url, data=json_test_string)

        resp_json = resp.json()

        exam_id = resp_json['id']

        for key in json_test_dict:
            self.assertTrue(json_test_dict[key] == resp_json[key])

        self.assertTrue('secret' in resp_json)
        self.assertTrue('wallet' not in resp_json)
        self.assertTrue('price' not in resp_json)

        get_exam_url = '{base_address}/exam/{exam_id}'
        url = get_exam_url.format(base_address=base_address, exam_id=exam_id)
        get_exam_response = requests.get(url)

        resp_json = get_exam_response.json()

        for key in json_test_dict:
            self.assertTrue(json_test_dict[key] == resp_json[key])

        self.assertTrue('secret' not in resp_json)
        self.assertTrue('wallet' not in resp_json)
        self.assertTrue('price' not in resp_json)

    def test_priced_exam_addition(self):
        json_test_string = '''{{
    "school": "Georgia Southern University",
    "class": "CSC1001",
    "file": "{blob_key}",
    "description":  "wallet_address",
    "professor" : "dr.ulrich",
    "free_or_nah" : false,
    "price": "1.00"
}}'''.format(blob_key=upload_blob())

        json_test_dict = json.loads(json_test_string)
        create_exam_url = '{base_address}/exam'
        base_address = 'http://127.0.0.1:8080'
        url = create_exam_url.format(base_address=base_address)
        resp = requests.post(url, data=json_test_string)

        resp_json = resp.json()

        exam_id = resp_json['id']

        for key in json_test_dict:
            self.assertTrue(json_test_dict[key] == resp_json[key])

        self.assertTrue('secret' in resp_json)
        self.assertFalse(resp_json['free_or_nah'])

        get_exam_url = '{base_address}/exam/{exam_id}'
        url = get_exam_url.format(base_address=base_address, exam_id=exam_id)
        get_exam_response = requests.get(url)

        resp_json = get_exam_response.json()

        for key in json_test_dict:
            self.assertTrue(json_test_dict[key] == resp_json[key])

        self.assertTrue('secret' not in resp_json)
        self.assertFalse(resp_json['free_or_nah'])

    def test_blob_upload(self):
        files = {'file': open('pic.jpg', 'rb')}

        base_address = 'http://127.0.0.1:8080'
        get_blob_upload_url = '{base_address}/generate_blobstore_url'

        resp = requests.get(get_blob_upload_url.format(base_address=base_address))

        upload_url = resp.text



        print "********************************"
        print upload_url

        resp = requests.post(upload_url, files=files)

        response_json = resp.json()


        get_blob_url = '{base_address}/blob/{blob_key}'

        url = get_blob_url.format(base_address=base_address, blob_key=response_json['blob_key'])
        response = requests.get(url, stream=True)
        with open('img.jpg', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)


        self.assertTrue(filecmp.cmp('img.jpg', 'pic.jpg'))








if __name__ == '__main__':
        unittest.main()






