##### DO NOT USE  REFERENCES ARE NOT PRESERVED #####
##### times out on HAPI test server so split into thirds and save.
from fhirclient.r4models import (
                                bundle,
                                 )
from json import loads, dumps
from requests import get, post, put
from datetime import datetime, date, timedelta
from pathlib import Path
from pprint import pprint, pformat

test_server = 'http://hapi.fhir.org/baseR4'

headers = {
    'Accept':'application/fhir+json',
    'Content-Type':'application/fhir+json',
    #"Authorization": 'Bearer 0QLWt38GQHyYxrcHuG40mw==',# TEMP meditech token remove and fix if this works
    }

base_path = '/Users/ehaas/Documents/FHIR/Davinci-Alerts/2020_09_hl7_connectathon/Synthea_Alert_Test_Data'

file_type = 'fhir'

file_size = '100Patients'

file = 'admit_notify-100r1.json'

mypath = Path() / base_path / file_type / file_size

myfile = mypath / file

print(f'My Path to Synthea Data a FHIR Bundle is {myfile}')
print()

ref_map = {
'Location': ('managingOrganization' , 'Organization'),
}

r_types = 'Patient','Practitioner','Organization','Location','Coverage','Encounter','Questionnaire','QuestionnaireResponse','Group'

for type in r_types:
    my_b = bundle.Bundle(loads(myfile.read_text()))
    print(f'Making the {type} Bundle')
    pop_list =  [i for i,e in enumerate(my_b.entry) if e.resource.resource_type != type]
    [my_b.entry.pop(i) for i in reversed(pop_list)]
    if type in list(ref_map.keys()):
        element = ref_map[type][0]
        old_ref = gettattr((getattr(type,element),'reference'))
        new_ref = old_ref.replace('urd:uuid:',ref_map[type][1])
        setattr((getattr(type,element),'reference', new_ref)
    print(type, len(my_b.entry) )
    if my_b.entry:
        out_file = f'argo-pl100r1-{type.lower()}-transaction-bundle.json'
        print(f'save {type} Bundle as argo-pl100r1-{type.lower()}-transaction-bundle.json' )
        my_out_file = mypath / out_file
        my_out_file.write_text(dumps(my_b.as_json()))
        print('...saved!')


#load to ref server
for f in mypath.iterdir():
    if f.name.startswith('argo-pl100r1'):
        with post(test_server,headers = headers, data=f.read_text() ) as r:
            print(f'posting {str(f)} to {test_server}...')
            print(r.status_code)
            if r.status_code > 200:
                print(dumps(r.json() ,indent=4))
