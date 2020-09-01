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

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'my secret key'

env = Environment(loader=FileSystemLoader('templates'))

#==============Globals======================

server_list =  {  # base_url for reference server - no trailing forward slash
    'FHIR R4': 'http://test.fhir.org/r4',
    'HAPI UHN R4': 'http://hapi.fhir.org/baseR4',
    'WildFHIR': 'http://wildfhir4.aegis.net/fhir4-0-1',
    }
base = 'FHIR R4'

# ================  Functions =================

def md_template(my_md,*args,**kwargs): # Create template with the markdown source text
    template = env.from_string(my_md,kwargs)
    # Render that template.
    app.logger.info(f'line 34: kwargs = {kwargs}')
    return template.render()

def search(Type, **kwargs):
    '''
    Search resource Tyype with parameters. [base]/[Type]{?params=kwargs}
    return resource as json
    '''
    headers = {
    'Accept':'application/fhir+json',
    'Content-Type':'application/fhir+json'
    }

    r_url = (f'{session["base"]}/{Type.capitalize()}')

    app.logger.info(f'line 50: r_url = {r_url}***')
    for attempt in range(5): #retry request up to ten times
        sleep(1)  # wait a bit between retries
        with get(r_url, headers=headers, params=kwargs) as r:
            # return r.status_code
            # view  output
            # return (r.json()["text"]["div"])
            if r.status_code <300:
                app.logger.info(f'query string = {r.url}')
                return r # just the first for now
    else:
        return None


def fetch(r_url):
    '''
    fetch resource by READ and return as request object
    '''
    headers = {
    'Accept':'application/fhir+json',
    'Content-Type':'application/fhir+json'
    }
    app.logger.info(f'****** r_url = {r_url}***')
    for attempt in range(5): #retry request up to ten times
        sleep(1)  # wait a bit between retries
        with get(r_url, headers=headers) as r:
            # return r.status_code
            # view  output
            # return (r.json()["text"]["div"])
            if r.status_code <300:
                return r # just the first for now
    else:
        return None

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

env = Environment(loader=FileSystemLoader('templates'))
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
        path = Path.cwd() / 'pages' / 'discovery.md' #markdown text with includes
        my_markdown_string=md_template(path.read_text(),server_list=session['server_list'], default=session['base_name'])
        return render_template('template.html',
            my_intro=my_intro,
            my_string=my_markdown_string,
            title="Discovery",
            current_time=datetime.datetime.now(),
            ht_offset = 0,
            seq_ht = 285,
        )

@app.route("/fetch-lists")
def fetch_lists():
    my_string='''## Server Returns a Bundle of User Facing Lists<br><br>Click on the blue buttons below to continue...'''
    # fetch all Groups
    requests_object = search("Group",_summary=True, type='person',) # requests object
    py_bundle = pyfhir(requests_object.json(), Type="Bundle")
    app.logger.info(f'bundle id = {py_bundle.id}')
    path = Path.cwd() / 'pages' / 'fetch_userfacinglists.md' #markdown text with includes
    my_markdown_string=md_template(path.read_text(),    user_facing_lists=py_bundle.entry,
     base_name=session['base_name'],
     url_string=requests_object.url ,
     )
    return render_template('template.html', my_intro=my_string,
        title="Returns a Bundle of User Facing Lists", current_time=datetime.datetime.now(),
        ht_offset = 285,
        seq_ht = 300,
        my_string=my_markdown_string,
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
        path = Path.cwd() / 'pages' / 'fetch_patientlist.md' #markdown text with includes
        session['md_string']=md_template(
             path.read_text(),
             base_name=session['base_name'],
             url_string=requests_object.url,
             )
    my_string='''## After Fetching the List of User Facing lists, a Patient list is selected using a simple Fetch operation: <br>Click on the blue buttons below to continue...'''
    return render_template('template.html',
        my_intro=my_string,
        title="Fetch Patient List",
        current_time=datetime.datetime.now(),
        ht_offset = 425,
        seq_ht = 425,
        my_string=session['md_string'],
        display_group_resource=True, # display Group resource
        Group = py_group
        )

@app.route("/fetch-more")
def fetch_more():
    endpoint = request.args.get('endpoint')
    app.logger.info(f'endpoint = {endpoint}')

    if endpoint:
        try:
            requests_object = fetch(endpoint) # requests object
            py_patient = pyfhir(requests_object.json(), Type="Patient") # request Patient object
        except AttributeError:
            app.logger.info(f'endpoint = {endpoint} is not a FHIR endpoint')
        else:
            for i in session['my_patients']:
                if i['id'] == py_patient.id:
                    i['dob'] = py_patient.birthDate.as_json()
                    i['sex'] = py_patient.gender
    else:
        requests_object = fetch(session['patientlist']) # requests Group object
        py_group = pyfhir(requests_object.json(), Type="Group")
        session['my_patients'] = []

        for i in py_group.member:
            e = i.entity
            patient_data=dict(
                display = getattr(e,'display', None),
                id = getattr(e,'reference', None) if getattr(e,'reference', None) == None else getattr(e,'reference', None).split('/')[-1]  ,
                inactive = getattr(i,'inactive', None),
            )
            session['my_patients'].append(patient_data)

    app.logger.info(f'my_patients = {session["my_patients"]}')
    my_string="## The User Get additional Patient data one of three ways: <br>Click on the blue buttons below to continue..."
    path = Path.cwd() / 'pages' / 'additional-data.md' #markdown text with includes
    my_markdown_string=md_template(
         path.read_text(),
         my_patients=session['my_patients'],
         session_base=session['base'],
         ep=endpoint
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
    return render_template('template.html', my_string="Foo",
        my_list=[6,7,8,9,10,11], title="Home", current_time=datetime.datetime.now())

@app.route("/about")
def about():
    path = Path.cwd() / 'pages' / 'about.md'

    return render_template('sub_template1.html', my_content=path.read_text(),
         title="About", current_time=datetime.datetime.now())

@app.route("/contact")
def contact():
    path = Path.cwd() / 'pages' / 'contact.md'

    return render_template('sub_template1.html', my_content=path.read_text(),
         title="Contact Info", current_time=datetime.datetime.now())

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    directory= f'{app.root_path}/test_output'
    return send_from_directory(directory= directory, filename=filename, as_attachment=True, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
    app.run(debug=True)
