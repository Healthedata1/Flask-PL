from flask import Flask, render_template, redirect, url_for, session, send_from_directory, request, Response
import sys, datetime, uuid
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

app = Flask(__name__,)
app.secret_key = 'my secret key'

env = Environment(loader=FileSystemLoader([f'{app.root_path}/pages',
            f'{app.root_path}/includes',]))

#==============Globals======================

server_list =  {  # base_url for reference server - no trailing forward slash
    'FHIR R4': 'http://test.fhir.org/r4',
    'HAPI UHN R4': 'http://hapi.fhir.org/baseR4',
    'WildFHIR': 'http://wildfhir4.aegis.net/fhir4-0-1',
    }
base = 'FHIR R4'
pages = f'{app.root_path}/pages'
group_characterstics = [
(0,'location','Location/[id]',),
(1,'attributed-to','Practitioner/[id]',),
(2,'attributed-to','Organization/[id]',),
(3,'team','Location/CareTeam/[id]',),
]

headers = {
    'Accept':'application/fhir+json',
    'Content-Type':'application/fhir+json'
    }
# ================  Functions =================

def md_template(my_md,*args,**kwargs): # Create template with the markdown source text
    template = env.get_template(my_md)
    # Render that template.
    app.logger.info(f'line 34: kwargs = {kwargs}')
    kwargs = {k.replace('__','-'):v for k,v in kwargs.items() }
    app.logger.info(f'line 34: kwargs = {kwargs}')
    return template.render(kwargs)

def search(Type, **kwargs):
    '''
    Search resource Type with parameters. [base]/[Type]{?params=kwargs}
    return resource as json, replace '__' with dashes
    '''

    app.logger.info(f'line 52: kwargs = {kwargs}')
    kwargs = {k.replace('__','-'):v for k,v in kwargs.items() }
    app.logger.info(f'line 54: kwargs = {kwargs}')
    r_url = (f'{session["base"]}/{Type.capitalize()}')

    app.logger.info(f'line 50: r_url = {r_url}***')
    for attempt in range(5): #retry request up to ten times
        sleep(1)  # wait a bit between retries
        with get(r_url, headers=headers, params=kwargs) as r:
            #app.logger.info(f'line 61:status = {r.status_code}') #return r.status_code
            #app.logger.info(f'line 62:body = {r.json()}')# view  output
            # return (r.json()["text"]["div"])
            if r.status_code <300:
                app.logger.info(f'line 65:query string = {r.url}')
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
            #app.logger.info(f'line 61:status = {r.status_code}') #return r.status_code
            #app.logger.info(f'line 62:body = {r.json()}')# view  output
            # return (r.json()["text"]["div"])
            if r.status_code <300:
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
            app.logger.info(f'line 105:status = {r.status_code}') #return r.status_code
            app.logger.info(f'line 106:body = {r.json()}')# view  output
            # return (r.json()["text"]["div"])
            if r.status_code <300:
                return r # just the first for now
    else:
        return None

# mockup for search by characteristic and value_reference
def mock_bychar(py_bundle, requests_url, c_code, c_value):
    url_string=f'{requests_url}&characteristic={c_code}&value_reference={c_value}'
    py_bundle.entry = [e for e in py_bundle.entry if e.resource.characteristic]
    py_bundle.entry = [e for e in py_bundle.entry if e.resource.characteristic[0].code == c_code and e.resource.characteristic[0].valueReference == c_value]
    return url_string,py_bundle


def update_pdata_table(bundle_dict): # update sessions['my_patients'] patient data table
    py_fhir = pyfhir(bundle_dict, Type="Bundle") # request Bundle
    for i in py_fhir.entry: #ignore paging for now TODO consider paging
        py_patient = i.resource
        update_pdata_row(py_patient)
    return

def update_pdata_row(py_patient):  # update sessions['my_patients'] for patient
    for i in session['my_patients']:
        if i['id'] == py_patient.id:
            i['dob'] = py_patient.birthDate.as_json()
            i['sex'] = py_patient.gender
    return


@app.template_filter()
def yaml(r_dict):
    return y_dump(r_dict, allow_unicode=True,)

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
            app.logger.info(f'line 64: base = {base}')
        app.logger.info(f'line 66: session = {session}')
        my_intro = '## The Client Searches for User Facing Patient Lists from an EHR by Querying the *Group* Endpoint...' # markdown intro since the svg doesn't play nice in markdown includes
        my_markdown_string=md_template('discovery.md',
            server_list=session['server_list'], default=session['base_name'],
            group_characterstics= group_characterstics,
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
    app.logger.info(f' line 166: request.form args = {dict(request.form)}') # get button value...
    if org_id: # fetch by managingEntity Groups
        requests_object = search("Group",_summary=True, type='person', managing__entity=f'Organization/{org_id}')
        url_string=requests_object.url

    elif char_id: # fetch by characteristic
        c_code = group_characterstics[int(char_id)][1]
        c_value = group_characterstics[int(char_id)][2].replace("[id]",input_id)
        #returns 400 error since characteristic not defined
        #instead will mock up by fetching all and sorting below
        # fetch all Groups
        '''
        requests_object = search("Group",_summary=True, type='person', characteristic=group_characterstics[int(char_id)][1],
        value__reference=group_characterstics[int(char_id)][2].replace('[id]',request.form.get("input_id")))
        url_string=requests_object.url
        '''
        requests_object = search("Group",_summary=True, type='person',) #

    else: # fetch all Groups
        requests_object = search("Group",_summary=True, type='person',) # requests object
        url_string=requests_object.url

    py_bundle = pyfhir(requests_object.json(), Type="Bundle")

    if char_id: #mock up by fetching by characteristic
        url_string, py_bundle = mock_bychar(py_bundle, requests_object.url, c_code, c_value)

    app.logger.info(f'bundle id = {py_bundle.id}')
    my_markdown_string=md_template('fetch_userfacinglists.md',    user_facing_lists=py_bundle.entry,
     base_name=session['base_name'],
     url_string=url_string,
     #params = params,
     )
    return render_template('details.html',
        my_intro=my_string,
        title="Returns a Bundle of User Facing Lists", current_time=datetime.datetime.now(),
        ht_offset = 285,
        seq_ht = 300,
        my_string=my_markdown_string,
        pyfhir = py_bundle
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
             )
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
    app.logger.info(f'endpoint = {endpoint}')
    added = False

    if endpoint:
        try:
            requests_object = fetch(endpoint) # requests object
            py_fhir = pyfhir(requests_object.json(), Type="Patient") # request Patient object
        except AttributeError:
            app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else:
            update_pdata_row(py_fhir)
            added = True
    elif include:
        try: requests_object = search('Group', _id=session["patientlist"].split("/")[-1], _include='Group:member')
        except AttributeError:
            app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else:
            update_pdata_table(requests_object.json())
            added = True
    elif multiple_or:
        p_value = ', Patient/'.join(i['id'] for i in session['my_patients'])
        p_value = f'Patient/{p_value}'
        try: requests_object = search('Patient', _id=p_value)
        except AttributeError:
            app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else:
            update_pdata_table(requests_object.json())
            added = True
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
            app.logger.info(f'line 310 BATCH body = {dumps(batch_body, indent=4)}')
        try:
            requests_object = post_batch(batch_body)
        except AttributeError:
                    app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else:
            update_pdata_table(requests_object.json())
    else:
        requests_object = fetch(session['patientlist']) # requests Group object
        py_fhir = pyfhir(requests_object.json(), Type="Group")
        session['my_patients'] = []

        for i in py_fhir.member: #type=Group
            e = i.entity
            patient_data=dict(
                display = getattr(e,'display', None),
                id = getattr(e,'reference', None) if getattr(e,'reference', None) == None else getattr(e,'reference', None).split('/')[-1]  ,
                inactive = getattr(i,'inactive', None),
            )
            session['my_patients'].append(patient_data)

    app.logger.info(f'my_patients = {session["my_patients"]}')
    my_string="## The User Get additional Patient data one of three ways: <br>Click on the blue buttons below to continue..."
    my_markdown_string=md_template(
         'additional-data.md',
         my_patients=session['my_patients'],
         session_base=session['base'],
         added=added,
         url_string=requests_object.url,
         request_headers = dumps(dict(requests_object.request.headers), indent=4),
         request_body = requests_object.request.body,
         response_headers = dumps(dict(requests_object.headers), indent=4),
         response_body=dumps(requests_object.json(), indent=4),
         group_id=session["patientlist"].split("/")[-1],
         )
    return render_template('template.html',
            my_intro=my_string,
            title="Fetch Additional Data",
            current_time=datetime.datetime.now(),
            ht_offset = 600,
            seq_ht = 825,
            my_string=my_markdown_string,
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
    return send_from_directory(directory= directory, filename=filename, as_attachment=True, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
    app.run(debug=True)
