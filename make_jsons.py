import zipfile
import csv
import json
import os
from io import BytesIO
import requests

STATIC_ROOT = os.environ.get('STATIC_ROOT', '/var/www')

CITY_FIELDS = {
    #'city_id': 0, # integer id of record in geonames database
    'name': 1, # name of geographical point (utf8) varchar(200)
    'ascii_name': 2, # name of geographical point in plain ascii characters, varchar(200)
    'alternate_names': 3, # alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
    'latitude': 4, #latitude in decimal degrees (wgs84)
    'longitude': 5, # longitude in decimal degrees (wgs84)
    #'feature_class': 6, # see http://www.geonames.org/export/codes.html, char(1)
    #'feature_code': 7, # see http://www.geonames.org/export/codes.html, varchar(10)
    'country_code': 8, # ISO-3166 2-letter country code, 2 characters
    #'cc2': 9, # alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
    #'admin1_code': 10, # fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
    #'admin2_code': 11, # code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80)
    #'admin3_code': 12, # code for third level administrative division, varchar(20)
    #'admin4_code': 13, # code for fourth level administrative division, varchar(20)
    #'population': 14, # bigint (8 byte int)
    #'elevation': 15, # in meters, integer
    #'dem': 16, # digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
    #'timezone': 17, # the iana timezone id (see file timeZone.txt) varchar(40)
    #'modification_date': 18, # date of last modification in yyyy-MM-dd format
}



countries = [(line[0],line[4]) for line in csv.reader(requests.get('http://download.geonames.org/export/dump/countryInfo.txt').text.splitlines(), dialect='excel-tab') if not line[0].startswith('#')]

with open('{}/countries.json'.format(STATIC_ROOT), 'w') as f:
    json.dump(countries, f)
for code, name in countries:
    req = requests.get('http://download.geonames.org/export/zip/{}.zip'.format(code))
    if req.status_code == 200:
        cities = []
        zipdata = BytesIO(req.content)
        myzipfile = zipfile.ZipFile(zipdata)
        for line in csv.reader(myzipfile.open('{}.txt'.format(code)).read().decode('utf-8').splitlines(), dialect='excel-tab'):
            city_data = {field: line[field_num] for field, field_num in CITY_FIELDS.items()}
            print('.', end='')
            cities.append(city_data)
        with open('{}/{}.json'.format(STATIC_ROOT, code), 'w') as f:
            json.dump(cities, f)


    


