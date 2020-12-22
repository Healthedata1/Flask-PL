'''bigger groups  create 3 orgs and 3 orgs and pract for each location keep locations for now  list  ME and locations.
better locations?
reference or url type - display
group narrative generation?







show extension as option?'''

import os, sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
# This allows you to import the desired function from the module hierarchy:
from fhirclient.r4models import (
                                            fhirdate,
                                            fhirreference,
                                            group,
                                            patient,
                                            organization,
                                            bundle,
                                            identifier,
                                            humanname,
                                            contactpoint,
                                            address,
                                            codeableconcept,
                                            coding,
                                            extension,
                                            questionnaireresponse as qr,
                                            meta,
                                             )
from json import loads, dumps
#from requests import get, post, put
from datetime import datetime, date, timedelta
from IPython.display import display as Display, HTML, Markdown
#from utils import bundle_me, to_json, to_yaml, get_id, load_transaction, validate, fetch_r
from pathlib import Path
from pprint import pprint, pformat
from nested_lookup import nested_lookup
from random import choice
#import FHIR_templates


#RENAME LOCATIONS
loc_map ={
'HALLMARK HEALTH SYSTEM' : [{'display': 'BAYSTATE FRANKLIN MEDICAL CENTER', 'reference': 'urn:uuid:bd7875ed-e7f7-4239-a6ec-61c4fed53751'}, {
"display": "HOLYOKE MEDICAL CENTER",
"reference": "urn:uuid:3806554c-0e8d-455b-b666-57511f0632d8"
},{
"display": "ST VINCENT HOSPITAL",
"reference": "urn:uuid:004a2230-c8b8-4b78-adc7-d37a44103a7f"
}],
'BEVERLY HOSPITAL CORPORATION' : [{'display': 'GOOD SAMARITAN MEDICAL CENTER', 'reference': 'urn:uuid:52e2b538-8ec8-4560-83b2-ab297d91ae17'}, {
"display": "SOUTH SHORE HOSPITAL",
"reference": "urn:uuid:5a8f14ef-d190-4e42-a802-283e227c1789"
}, {
"display": "NORTH SHORE MEDICAL CENTER",
"reference": "urn:uuid:76785e60-5f8b-4782-903b-78bcfc9da9b1"
}],
'CAMBRIDGE HEALTH ALLIANCE' : [{'display': 'BETH ISRAEL DEACONESS HOSPITAL - PLYMOUTH', 'reference': 'urn:uuid:33b34318-015b-450a-ab5f-4e8b66b2654b'},{
"display": "CARNEY HOSPITAL",
"reference": "urn:uuid:17293a8b-eb43-4fad-93e8-58479f814bb5"
},{
"display": "BRIGHAM AND WOMEN'S HOSPITAL",
"reference": "urn:uuid:a0f2968c-87c3-420b-88eb-63f1484c19cc"
}],
}

pract_map = {
'HALLMARK HEALTH SYSTEM' : [{
"display": "Dr. Adriana394 Dickinson688",
"reference": "urn:uuid:0000016f-64f5-9833-0000-000000000096"
},{
"display": "Dr. Francie486 Marks830",
"reference": "urn:uuid:0000016f-64f5-9833-0000-0000000001a4"
},{
"display": "Dr. Corinna386 Beer512",
"reference": "urn:uuid:0000016f-64f5-9833-0000-0000000000c8"
}],
'BEVERLY HOSPITAL CORPORATION' : [{
"display": "Dr. Kira861 Mayert710",
"reference": "urn:uuid:0000016f-64f5-9833-0000-00000000019a"
},{
"display": "Dr. Jaime666 Paredes726",
"reference": "urn:uuid:0000016f-64f5-9833-0000-0000000000be"
}, {
"display": "Dr. Carmelia328 Walter473",
"reference": "urn:uuid:0000016f-64f5-9833-0000-00000000017c"
}],
'CAMBRIDGE HEALTH ALLIANCE' : [{
"display": "Dr. Ressie457 Wyman904",
"reference": "urn:uuid:0000016f-64f5-9833-0000-0000000000f0"
},{
"display": "Dr. Sharan181 Reichel38",
"reference": "urn:uuid:0000016f-64f5-9833-0000-000000000082"
},{
"display": "Dr. Johnetta529 Kiehn525",
"reference": "urn:uuid:0000016f-64f5-9833-0000-0000000001cc"
}],
}


base_path = '/Users/ehaas/Documents/FHIR/Davinci-Alerts/2020_09_hl7_connectathon/Synthea_Alert_Test_Data'

file_type = 'fhir'
#file_type = 'csv'


#file_size = '3Patients'
file_size = '100Patients'

#file = 'admit_notify-2.json'
file = 'admit_notify-100.json'

myfile = Path() / base_path / file_type / file_size / file

print(f'My Path to Synthea Data a FHIR Bundle is {myfile}')
print()

my_b = bundle.Bundle(loads(myfile.read_text()))

#check if all Coverage.beneficiary resolve in bundle
counter = 0
my_ref = [i.fullUrl for i in my_b.entry if i.resource.resource_type == "Patient"]
print(my_ref)
counter = 0
del_me = []
for i,e in enumerate(my_b.entry):
    r = e.resource
    if r.resource_type == 'Coverage' and r.beneficiary.reference not in my_ref:
        print(f'{counter}/{i}). Coverage {e.fullUrl} benificiary {r.beneficiary.reference} does not resolve')
        del_me.append(i)
    if r.resource_type == 'Encounter' and r.subject.reference not in my_ref:
        print(f'{counter}/{i}). Coverage {e.fullUrl} benificiary {r.subject.reference} does not resolve')
        del_me.append(i)
    counter +=1
print(del_me)
for i in reversed(del_me):
    goner = my_b.entry.pop(i)
    print(f'{goner.resource.resource_type}/{goner.resource.id}')
print(f'size={len(my_b.entry)}')

print(my_b.resource_type, len(my_b.entry))
bundle_index = [0,0,0]
counter = 0
for i,e in enumerate(my_b.entry):
    r = e.resource
    # add tag
    try:
        r.meta.tag[0].code = "2020-Sep"
    except TypeError:
        r.meta.tag = []
        r.meta.tag.append(coding.Coding({'code':'2020-Sep'}))
    except AttributeError:
        r.meta = meta.Meta({'tag':[{'code':'2020-Sep'}]})
    if r.resource_type == 'Encounter':
            print(f'{counter}/{i}). r.serviceProvider = {r.serviceProvider.as_json()}')
            if counter <30:
                r.serviceProvider = fhirreference.FHIRReference({'display': 'HALLMARK HEALTH SYSTEM', 'reference': 'urn:uuid:d692e283-0833-3201-8e55-4f868a9c0736'})
                r.location[0].location= fhirreference.FHIRReference(choice(loc_map['HALLMARK HEALTH SYSTEM']))
                r.participant[0].individual= fhirreference.FHIRReference(choice(pract_map['HALLMARK HEALTH SYSTEM']))
                bundle_index[0] = i

            elif counter <60:
                r.serviceProvider = fhirreference.FHIRReference({'display': 'BEVERLY HOSPITAL CORPORATION', 'reference': 'urn:uuid:37c0de84-bcaf-3624-82bf-a89b2ac441b8'})
                r.location[0].location= fhirreference.FHIRReference(choice(loc_map['BEVERLY HOSPITAL CORPORATION']))
                r.participant[0].individual= fhirreference.FHIRReference(choice(pract_map['BEVERLY HOSPITAL CORPORATION']))
                bundle_index[1] = i
            else:
                r.serviceProvider = fhirreference.FHIRReference({'display': 'CAMBRIDGE HEALTH ALLIANCE', 'reference': 'urn:uuid:e002090d-4e92-300e-b41e-7d1f21dee4c6'})
                r.location[0].location= fhirreference.FHIRReference(choice(loc_map['CAMBRIDGE HEALTH ALLIANCE']))
                r.participant[0].individual= fhirreference.FHIRReference(choice(pract_map['CAMBRIDGE HEALTH ALLIANCE']))
                bundle_index[2] = i
            counter +=1

print(bundle_index)
'''
counter = 0
for i,e in enumerate(my_b.entry):
    r = e.resource
    if r.resource_type == 'Encounter':
        if r.location[0].location.display in list(loc_map.keys()):
            r.location[0].location =  fhirreference.FHIRReference(loc_map[r.location[0].location.display])
            print(f'{counter}/{i}). r.serviceProvider = {r.serviceProvider.as_json()}')
            print(f'{counter}/{i}). r.location[0].location = {r.location[0].location.as_json()}')
            counter +=1
counter = 0
'''
for i,e in enumerate(my_b.entry):
    r = e.resource
    if r.resource_type == 'Encounter':
            print(f'{counter}/{i}). r.serviceProvider = {r.serviceProvider.as_json()}')
            print(f'{counter}/{i}). r.participant[0].individual = {r.participant[0].individual.as_json()}')
            print(f'{counter}/{i}). r.location[0].location = {r.location[0].location.as_json()}')
            counter +=1

'''print(my_b.type)
for i,e in enumerate(my_b.entry):
    r = e.resource
    print(f'{i}. Type = {r.resource_type}')

print(f'size={len(my_b.entry)}')
pprint ([f"{x.resource.resource_type}/{x.resource.id}" for x in my_b.entry])'''


'''
#### resort bundle for transaction:
r_types = 'Patient','Practitioner','Organization','Location','Coverage','Encounter','Questionnaire','QuestionnaireResponse','Group'

my_b.entry.sort(key=lambda x: t_types.index(x.resource.resource_type))
print(f'size={len(my_b.entry)}')
pprint ([f"{x.resource.resource_type}/{x.resource.id}" for x in my_b.entry])
'''


####WRITE#######

#file = 'admit_notify-2.json'

##### times out on HAPI test server so split bundle and into thirds
for i,j in enumerate(bundle_index):
    print(i,j)
    new_bundle = bundle.Bundle(my_b.as_json())
    print(len(new_bundle.entry))
    file = f'admit_notify-100-{list(loc_map.keys())[i]}.json'

    print(file)
    if i == 0:
        b = range(0,j)
    else:
        b = range(bundle_index[i-1],j)

    print(b)
    new_bundle.entry = [my_b.entry[index] for index in b]
    print(len(new_bundle.entry))
    print('---')
    myfile = Path() / base_path / file_type / file_size / file
    myfile.write_text(dumps(new_bundle.as_json()), encoding='utf-8')

'''
print(my_b.type)
for i,e in enumerate(my_b.entry):
    r = e.resource
    print(f'{i}. Type = {r.resource_type}')

print(f'size={len(my_b.entry)}')
pprint ([f"{x.resource.resource_type}/{x.resource.id}" for x in my_b.entry])
'''
#### Write entire bundle
#### resort bundle for transaction:
r_types = 'Patient','Practitioner','Organization','Location','Coverage','Encounter','Questionnaire','QuestionnaireResponse','Group'

my_b.entry.sort(key=lambda x: r_types.index(x.resource.resource_type))
print(f'size={len(my_b.entry)}')
pprint ([f"{x.resource.resource_type}/{x.resource.id}" for x in my_b.entry])
file = 'admit_notify-100r1.json'
myfile = Path() / base_path / file_type / file_size / file
myfile.write_text(dumps(my_b.as_json()), encoding='utf-8')

myfile.read_text(encoding='utf-8')

print("DONE!!")
