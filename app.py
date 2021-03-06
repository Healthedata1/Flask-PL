from flask import Flask, render_template, redirect, url_for, session, send_from_directory, request, Response
import sys, datetime, uuid, os
from json import load, dumps, loads
from requests import get, post, put
from commonmark import commonmark
from importlib import import_module
from pathlib import Path
from copy import deepcopy
import fhirclient.r4models.meta as M
import fhirclient.r4models.fhirdate as FD
import fhirclient.r4models.bundle as B
from utils import write_out, clear_dir, read_in
from time import sleep
from jinja2 import Environment, FileSystemLoader
from yaml import dump as y_dump
import logging

logging.basicConfig(
        level=logging.DEBUG,
        #filename='/Users/ehaas/Documents/Python/Flask-PL/demo.log',
        format='[%(asctime)s] %(levelname)s in %(module)s %(lineno)d}: %(message)s',
        )

app = Flask(__name__,)
#app.config["DEBUG"] = True
app.secret_key = 'my secret key'

env = Environment(loader=FileSystemLoader([f'{app.root_path}/pages',
            f'{app.root_path}/includes',]))

app.logger.info("Starting Program ....")
app.logger.info(f"Process ID = {os.getpid()}")
#==============Globals======================

server_list =  {  # base_url for reference server - no trailing forward slash
    'FHIR R4': 'http://test.fhir.org/r4',
    'HAPI UHN R4': 'http://hapi.fhir.org/baseR4',
    'WildFHIR': 'http://wildfhir4.aegis.net/fhir4-0-1',
    'Meditech':  'https://dev-mtx-interop.meditech.com/v1/ArgoPatientList/R4',
    'Cerner': 'https://fhir-open.stagingcerner.com/beta/dacc6494-e336-45ad-8729-b789ff8663c6',
    }

base = 'HAPI UHN R4'
pages = f'{app.root_path}/pages'
group_characteristics = [
(0,'location','Location/[id]','33b34318-015b-450a-ab5f-4e8b66b2654b',),
(1,'practitioner','Practitioner/[id]','0000016f-57cb-cdac-0000-00000000014a',),
(2,'organization','Organization/[id]', '...'),
(3,'team','Location/CareTeam/[id]','...'),
]

headers = {
    'Accept':'application/fhir+json',
    'Content-Type':'application/fhir+json',
    "Authorization": 'Bearer Ul5Jq6jHSqOIuud7KMrrag==',# TEMP meditech token remove and fix if this works
    }

profile_urls = {
'pl':'http://www.fhir.org/guides/argonaut/patient-list/StructureDefinition/patientlist',
'q_ext':'http://www.fhir.org/guides/argonaut/patient-list/StructureDefinition/patientlist-questionnaire',
'qr_ext':'http://www.fhir.org/guides/argonaut/patient-list/StructureDefinition/patientlist-questionnaireresponse',
'appt_ext':'http://www.fhir.org/guides/argonaut/patient-list/StructureDefinition/patientlist-appointment',
'enc_ext':'http://www.fhir.org/guides/argonaut/patient-list/StructureDefinition/patientlist-encounter',
}

download_types = dict(
endpoint = 'Patient',
qr = 'Bundle',
multiple_or = 'Bundle',
batch = 'Bundle',
include = 'Bundle',
qrbonus = 'Bundle',
appt_ext = 'Appointment',
enc_ext = 'Encounter',
)

tag = '2021-Jan'
# ================  Functions =================

def md_template(my_md,*args,**kwargs): # Create template with the markdown source text
    template = env.get_template(my_md)
    # Render that template.
    #app.logger.info(f' kwargs = {kwargs}')
    kwargs = {k.replace('__','-'):v for k,v in kwargs.items() }
    #app.logger.info(f' kwargs = {kwargs}')
    return template.render(kwargs)

def search(Type, **kwargs):
    '''
    Search resource Type with parameters. [base]/[Type]{?params=kwargs}
    return resource as json, replace '__' with dashes
    '''
    #app.logger.info(f' kwargs = {kwargs}')
    if session['base_name']=='HAPI UHN R4' and Type == "Group": # append tag search param
        kwargs['_tag'] = tag
    #app.logger.info(f' kwargs = {kwargs}')
    kwargs = {k.replace('__','-'):v for k,v in kwargs.items() }
    #app.logger.info(f' kwargs = {kwargs}')
    r_url = (f'{session["base"]}/{Type}')

    app.logger.info(f' r_url = {r_url}***')
    for attempt in range(5): #retry request up to ten times
        sleep(1)  # wait a bit between retries
        with get(r_url, headers=headers, params=kwargs) as r:
            app.logger.info(f'url-string = {r.url}')
            app.logger.info(f'status = {r.status_code}') #return r.status_code
            #app.logger.info(f'body = {r.json()}')# view  output
            #app.logger.info(f'body as json = {dumps(r.json(), indent=4)}')# view  output
            # return (r.json()["text"]["div"])
            if r.status_code <300:
                app.logger.info(f'query string = {r.url}')
                #app.logger.info(f'bundle entry count = {r.json()["total"]}')
                session['entry_count']= r.json()["total"]
                app.logger.info(f'bundle entry count = {session["entry_count"]}')
                app.logger.info(f'sys.getsizeof(r.json()) = {sys.getsizeof(r.json())}')
                bundle_to_file(r.json(),)
                return r # just the first for now
    else:
        return None


def fetch(r_url):
    '''
    fetch resource by READ and return as request object
    '''
    app.logger.info(f'****** r_url = {r_url}***')
    for attempt in range(5): #retry request up to ten times
        sleep(1)  # wait a bit between retries
        with get(r_url, headers=headers) as r:
            app.logger.info(f'status = {r.status_code}') #return r.status_code
            # app.logger.info(f'body = {r.json()}')# view  output
            # return (r.json()["text"]["div"])
            if r.status_code <300:
                bundle_to_file(r.json(),type=r.json()['resourceType'].lower())
                return r # just the first for now
    else:
        return None

def post_batch(data):
    '''
    POST Batch as dict GET request and return response object
    '''
    r_url = session["base"]
    for attempt in range(5): #retry request up to ten times
        sleep(1)  # wait a bit between retries
        with post(r_url, headers=headers, data=dumps(data)) as r:
            app.logger.info(f'status = {r.status_code}') #return r.status_code
            #app.logger.info(f'body = {r.json()}')# view  output
            # return (r.json()["text"]["div"])
            if r.status_code <300:
                return r # just the first for now
    else:
        return None

# mockup for search by characteristic and value_reference
def mock_bychar(dict_bundle, c_value):
    '''
    The summary from the test servers do not include characteristic element: to determine if value-reference is a match get each full resource in Bundle and look at characteristic valueReference to decide if stays in Bundle
    '''
    py_bundle = pyfhir(dict_bundle, Type="Bundle")
    #app.logger.info(f'resourceType={py_bundle.resource_type}, len = {len(py_bundle.entry)}')
    remove_me = []
    for i,e in enumerate(py_bundle.entry):
        group_dict = fetch(e.fullUrl).json() #get Group
        #app.logger.info(f'py_group = {dumps(group_dict, indent = 4)}')
        py_group = pyfhir(group_dict, Type="Group")#convert to pyfhir
        if [c.valueReference.reference for c in py_group.characteristic if
                c.valueReference.reference == c_value]: #just the first one for now
            #app.logger.info(f'py_group.characteristic.valueReference: { [c.valueReference.reference for c in py_group.characteristic]}== {c_value}')
            pass
        else:
            #app.logger.info(f'py_group.characteristic.valueReference: { [c.valueReference.reference for c in py_group.characteristic]}  != {c_value}')
            remove_me.append(i)
    py_bundle.total = len(py_bundle.entry)-len(remove_me)
    for i in reversed(remove_me):
        py_bundle.entry.pop(i)
    return py_bundle.as_json()


def update_pdata_table(bundle_dict): # update sessions['my_patients'] patient data table
    py_fhir = pyfhir(bundle_dict, Type="Bundle") # request Bundle
    for i in py_fhir.entry: #ignore paging for now TODO consider paging
        py_patient = i.resource
        update_pdata_row(py_patient)
    return

def update_pdata_row(py_patient):  # update sessions['my_patients'] for patient
    app.logger.info(f'before updating session["my_patients"] = {session["my_patients"]}')
    for i in session['my_patients']:
        if i['id'] == py_patient.id:
            i['dob'] = py_patient.birthDate.as_json()
            i['sex'] = py_patient.gender
            session.modified = True
    app.logger.info(f'after updating session["my_patients"] = {session["my_patients"]}')
    return


def get_ext_ref(member_index,ext_url): #get extension value and type from member based on ext_url
    app.logger.info(f'member_index = {member_index} of type = {type(member_index)}')

    path =  Path () / app.root_path / 'test_output' / 'test-argo-pl-group.json'
    group_dict = loads(path.read_text())
    try:
        member_ext = group_dict['member'][member_index]['extension']
    except KeyError:
        member_ext = group_dict['member'][member_index]['entity']['extension']
    for i in member_ext:
        app.logger.info(f'{[i["url"]]}' )
        app.logger.info(f'{ext_url}' )
        app.logger.info(f'{profile_urls}' )
    ref_id = (i['valueReference']['reference'] for i in member_ext if i['url'] == profile_urls[ext_url])
    return next(ref_id)


def bundle_to_file(dict_bundle, type='bundle'):
    write_out(app.root_path, f"test-argo-pl-{type}.json", dumps(dict_bundle, indent=4))
    write_out(app.root_path, f"test-argo-pl-{type}.yml", y_dump(dict_bundle, sort_keys=False))


@app.template_filter()
def yaml(r_dict):
    return y_dump(r_dict, allow_unicode=True, sort_keys=False)

@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """convert a datetime to a different format."""
    return value.strftime(format)

@app.template_filter()
def markdown(text, *args, **kwargs):
    return commonmark(text, *args, **kwargs,)

env.filters['yaml'] = yaml

app.jinja_env.filters['datetimefilter'] = datetimefilter
app.jinja_env.filters['markdown'] = markdown
app.jinja_env.filters['yaml'] = yaml

def pyfhir(r_dict, Type=None):
    '''
    input is resource instance as r_dict
    output is fhirclient class instance
    '''
    type = Type if Type else r_dict['resourceType']
    MyClass = getattr(import_module(f"fhirclient.r4models.{type.lower()}"),type)
    # Instantiate the class (pass arguments to the constructor, if needed)
    instance = MyClass(r_dict, strict=False)
    return(instance)

@app.route("/")
def intro():
    session['server_list'] = server_list
    session['base_name'] = base
    session['base'] = next(server_list[i] for i in server_list if i==base)
    my_string="### The Argo Patient List client application will cover some foundational, early-design operations such as list discovery, selecting list member records, and selection of 'extra' patient data using various methods. Including initial Testing of the discovery, and fetching of patients lists and associated data using the FHIR RESTful API.<br><br>Click on the blue buttons below to get started..."
    return render_template('template.html', my_intro=my_string,
        title="Index", current_time=datetime.datetime.now(),
        ht_offset = 0,
        seq_ht = 285,
        )

@app.route("/discovery", methods=["POST", "GET"])
def discovery():
        if request.method == 'POST':
            #get base
            session['base'] = request.form["get-server"]
            session['base_name'] = next(i for i in server_list if server_list[i]==session['base'])
            app.logger.info(f'base = {base}')
        app.logger.info(f'session = {session}')
        my_intro = '## The Client Searches for User Facing Patient Lists from an EHR by Querying the *Group* Endpoint...' # markdown intro since the svg doesn't play nice in markdown includes
        my_markdown_string=md_template('discovery.md',
            server_list=session['server_list'], default=session['base_name'],
            group_characteristics=group_characteristics,
            )
        return render_template('template.html',
            my_intro=my_intro,
            my_string=my_markdown_string,
            title="Discovery",
            current_time=datetime.datetime.now(),
            ht_offset = 0,
            seq_ht = 285,
        )

@app.route("/fetch-lists", methods=["POST", "GET"])
def fetch_lists():
    org_id = request.form.get("organization_id")
    char_id = request.form.get("characteristic")
    input_id = request.form.get("input_id")
    my_string='''## Server Returns a Bundle of User Facing Lists<br><br>Click on the blue buttons below to continue...'''
    app.logger.info(f'request.form args = {dict(request.form)}') # get button value...
    if org_id: # fetch by managingEntity Groups
        requests_object = search(
        "Group",
        _summary='true',
        _count=50,
         type='person',
          managing__entity=f'Organization/{org_id}'
          )
        url_string=requests_object.url
        dict_bundle = requests_object.json()

    elif char_id is not None: # fetch by characteristic
        c_code = group_characteristics[int(char_id)][1]
        c_value = group_characteristics[int(char_id)][2].replace("[id]",input_id)
        requests_object = search(
        "Group",
        _summary='true',
        _count=50,
        type='person',
        characteristic=c_code,
        value__reference=c_value
        )
        # Assume search by value-ref supported
        try:
            url_string=requests_object.url
            dict_bundle = requests_object.json()
        except AttributeError as e:
            app.logger.error(f'{e} , try search without sp value-reference')
            requests_object = search(
            "Group",
            _summary='true',
            _count=50,
            type='person',
            characteristic=c_code,
            #value__reference=c_value
            )
            url_string=f'{requests_object.url}&value-reference={c_value.replace}'
            dict_bundle = mock_bychar(dict_bundle=requests_object.json(),c_value=c_value) #filter entries in bundle by value-reference

    else: # fetch all Groups
        requests_object = search(
        "Group",
        _summary='true',
        type='person',
        _count=50,
         ) # requests object
        url_string=requests_object.url
        dict_bundle = requests_object.json()

    #bundle_to_file(dict_bundle)
    py_bundle = pyfhir(dict_bundle, Type="Bundle")

    app.logger.info(f'bundle id = {py_bundle.id}')
    my_markdown_string=md_template('fetch_userfacinglists.md',
     user_facing_lists=py_bundle.entry,
     base_name=session['base_name'],
     url_string=url_string,
     count = session['entry_count'],
     #params = params,
     )
    return render_template('details.html',
        my_intro=my_string,
        title="Returns a Bundle of User Facing Lists", current_time=datetime.datetime.now(),
        ht_offset = 285,
        seq_ht = 300,
        my_string=my_markdown_string,
        pyfhir = py_bundle,
        )

@app.route("/fetch-patientlist", methods=["POST", "GET"])
def fetch_patientlist():
    if request.method == 'POST':
        session['patientlist'] = request.form["get-list"]
        app.logger.info(f'session["patientlist"]= {session["patientlist"]}')
        requests_object = fetch(session['patientlist']) # requests object
        write_out(app.root_path, "test-argo-pl-group.json", dumps(requests_object.json(), indent=4))
        write_out(app.root_path, "test-argo-pl-group.yml", yaml(requests_object.json()))
        py_group = pyfhir(requests_object.json(), Type="Group")
        app.logger.info(f'group id = {py_group.id}')
        session['md_string']=md_template(
             'fetch_patientlist.md',
             base_name=session['base_name'],
             url_string=requests_object.url,
             count=requests_object.json()['quantity']
             )
        session["use_case"] = "endpoint"
    my_string='''## After Fetching the List of User Facing lists, a Patient list is selected using a simple Fetch operation: <br>Click on the blue buttons below to continue...'''
    return render_template('group_details.html',
        my_intro=my_string,
        title="Fetch Patient List",
        current_time=datetime.datetime.now(),
        ht_offset = 425,
        seq_ht = 425,
        my_string=session['md_string'],
        pyfhir = py_group
        )

@app.route("/fetch-more")
def fetch_more():
    endpoint = request.args.get('endpoint')
    multiple_or = request.args.get('multipleOr')
    batch = request.args.get('batch')
    include = request.args.get('include')
    qr = request.args.get('qr')
    my_ext = request.args.get("my_ext") # enc_ext or appt_ext
    app.logger.info(f'endpoint = {endpoint}')
    added = False
    session["scroll"] = None


    if endpoint:
        try:
            requests_object = fetch(endpoint) # requests object
            py_fhir = pyfhir(requests_object.json(), Type="Patient") # request Patient object
        except AttributeError:
            app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else:
            update_pdata_row(py_fhir)
            added = True
            session['scroll']='endpoint'
    elif include:
        try: requests_object = search('Group', _id=session["patientlist"].split("/")[-1], _include='Group:member')
        except AttributeError:
            app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else:
            update_pdata_table(requests_object.json())
            added = True
            #bundle_to_file(requests_object.json())
            session['scroll']='include'
    elif multiple_or:
        p_value = ', Patient/'.join(i['id'] for i in session['my_patients'])
        p_value = f'Patient/{p_value}'
        try: requests_object = search('Patient', _id=p_value)
        except AttributeError:
            app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else:
            update_pdata_table(requests_object.json())
            added = True
            session['scroll']='multiple_or'
    elif batch:
        batch_body = {
          "resourceType": "Bundle",
          "type": "batch",
          "entry":[],
        }
        for i in session['my_patients']:
            entry = {
                "request": {
                "method": "GET",
                "url": f"Patient/{i['id']}"
              }
            }
            batch_body['entry'].append(entry)
            app.logger.info(f'BATCH body = {dumps(batch_body, indent=4)}')
        try:
            requests_object = post_batch(batch_body)
        except AttributeError:
                    app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else:
            update_pdata_table(requests_object.json())
            added = True
            session['scroll']='batch'

    elif qr:  # fetch Q and QR qr == member_index
        member_index = int(request.args.get('member-index'))
        qr_id = get_ext_ref(member_index = member_index, ext_url='qr_ext')
        qr_id = qr_id.split('/')[-1]
        try:
            requests_object = search('QuestionnaireResponse', _id=qr_id, _include='QuestionnaireResponse:questionnaire')
            app.logger.info(f'requests_object.json() = {requests_object.json()}')
            py_fhir = pyfhir(requests_object.json(), Type="Bundle") # request Bundle object
        except AttributeError:
            app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else: # get qr data
            for entry in py_fhir.entry:
                if entry.resource.resource_type == "QuestionnaireResponse":
                    my_qr = entry.resource
                    answer_list = []
                    for i in my_qr.item:# assume list items go one deep for know - recurse later:
                        answer = i.answer[0].as_json()
                        answer_list.append(answer)
            #update_pdata_row
            session['my_patients'][member_index]['answer_list']=answer_list
            session['scroll']='qr'
            session.modified = True
            app.logger.info(f"session['my_patients']={session['my_patients']}")

    elif my_ext:  # fetch enc_ext and appt_ext data
        data = []
        member_index = int(request.args.get('member-index'))
        ref_id = get_ext_ref(member_index=member_index, ext_url=my_ext)
        data.append(ref_id)
        try:
            requests_object = fetch(f'{session["base"]}/{ref_id}')
            app.logger.info(f'requests_object.json() = {requests_object.json()}')
            py_fhir = pyfhir(requests_object.json())
        except AttributeError:
            app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else: # get timedata
            if py_fhir.resource_type == "Encounter":
                data.append(py_fhir.status)
                data.append(py_fhir.class_fhir.display)
                try:
                    data.append(py_fhir.period.start.as_json())
                except AttributeError:
                    data.append("NA")
                try:
                    data.append(py_fhir.participant[0].individual.display)
                except TypeError:
                    data.append("NA")
                try:
                    data.append(f'{py_fhir.location[0].location.reference} ({py_fhir.location[0].location.display})')
                except AttributeError:
                    data.append(py_fhir.location[0].location.reference)

            elif py_fhir.resource_type == "Appointment":
                data.append(py_fhir.start.as_json())
                data.append(py_fhir.participant[0].actor.display)
                data.append(py_fhir.status)
            #update_pdata_row
            session['my_patients'][member_index][f'{my_ext}_data']=data
            session['scroll']= my_ext
            session.modified = True
            app.logger.info(f"session['my_patients']={session['my_patients']}")

    else:
        requests_object = fetch(session['patientlist']) # requests Group object
        py_fhir = pyfhir(requests_object.json(), Type="Group")
        session['my_patients'] = []
        # remove q_list from the session if it is there
        try:
            session.pop('q_list')
        except KeyError:
            pass

        for i in py_fhir.member[:10]: #type=Group
            e = i.entity
            patient_data=dict(
                display = getattr(e,'display', None),
                id = getattr(e,'reference', None) if getattr(e,'reference', None) == None else getattr(e,'reference', None).split('/')[-1]  ,
                inactive = getattr(i,'inactive', None),
            )
            session['my_patients'].append(patient_data)

        # check what if any member extensions - just looking at first member for now
        for ext_type in list(profile_urls.keys())[2:]:
            session[f'{ext_type}_exist'] = False
            try:
                for check_ext in py_fhir.member[0].extension:
                    app.logger.info(f'check_ext.url == profile_urls[ext_type] : {check_ext.url} == {profile_urls[ext_type]}')
                    if check_ext.url == profile_urls[ext_type]:
                        session[f'{ext_type}_exist'] = True
            except KeyError:  # no members
                pass


        # if Q Extension get questions assume only one for now
        try:
            ext = py_fhir.extension[0]
        except TypeError:
            app.logger.info ('No Q extension for Group/{py_fhir}') # no extesnsion
        else:
            session['q_ref'] = ext.valueReference.reference
            app.logger.info(f'ext.valueReference.reference = {session["q_ref"]}')
            myq = fetch(f'{session["base"]}/{session["q_ref"]}')
            py_q = pyfhir(myq.json(), Type="Questionnaire")
            app.logger.info(f'py_q.id = {py_q.id}')
            session['q_list'] = []
            for q_item in py_q.item:
                question = q_item.text
                session['q_list'].append(question)

    app.logger.info(f'my_patients = {session["my_patients"]}')
    my_string="## The User Get additional Patient data one of three ways: <br>Click on the blue buttons below to continue..."
    try:
        request_body = dumps(loads(requests_object.request.body), indent=4)
    except TypeError:
        request_body = requests_object.request.body
    except AttributeError:
        request_body = None
    #app.logger.info(f'request_body = {request_body}')
    app.logger.info(f'session = {session}')
    my_markdown_string=md_template(
         'additional-data.md',
         my_patients= session.get('my_patients'),
         session_base=session.get('base'),
         session_q=session.get('q_ref'),
         q_list = session.get('q_list'),
         qr_ext_exist=session.get('qr_ext_exist'),
         appt_ext_exist=session.get('appt_ext_exist'),
         enc_ext_exist=session.get('enc_ext_exist'),
         added=added,
         scroll = session['scroll'],
         url_string=requests_object.url,
         request_headers = dumps(dict(requests_object.request.headers), indent=4),
         request_body = request_body,
         response_headers = dumps(dict(requests_object.headers), indent=4),
         response_body=dumps(requests_object.json(), indent=4),
         group_id=session.get("patientlist").split("/")[-1],
         download_types=download_types,
         )
    return render_template('template.html',
            my_intro=my_string,
            title="Fetch Additional Data",
            current_time=datetime.datetime.now(),
            ht_offset = 600,
            seq_ht = 825,
            my_string=my_markdown_string,
        )

@app.route("/todo")
def todo():
    return render_template('todo.html',
            my_intro='## TODO...Click the back button or the "Argo Patient List!" link to start over',
            title="TODO",
            current_time=datetime.datetime.now(),
        )

@app.route("/home")
def home():
    return redirect('/')

@app.route("/about")
def about():
    path = Path(pages) / 'about.md'
    return render_template('sub_template1.html', my_content=path.read_text(),
         title="About", current_time=datetime.datetime.now())

@app.route("/contact")
def contact():
    path = Path(pages) / 'contact.md'
    return render_template('sub_template1.html', my_content=path.read_text(),
         title="Contact Info", current_time=datetime.datetime.now())

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    directory= f'{app.root_path}/test_output'
    return send_from_directory(directory=directory, filename=filename, as_attachment=True, cache_timeout=0)

if __name__ == '__main__':
    app.run(debug=True)
