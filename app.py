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

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'my secret key'

@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """convert a datetime to a different format."""
    return value.strftime(format)

@app.template_filter()
def markdown(text, *args, **kwargs):
    return commonmark(text, *args, **kwargs)

app.jinja_env.filters['datetimefilter'] = datetimefilter
app.jinja_env.filters['markdown'] = markdown

@app.route("/")
def intro():
    my_string="**The Argo Patient List client application will cover some foundational, early-design operations such as list discovery, selecting list member records, and selection of 'extra' patient data using various methods. Including initial Testing of the discovery, and fetching of patients lists and associated data using the FHIR RESTful API.<br>Click on the blue buttons below to get started...**"
    path = Path.cwd() / 'static' / 'images' / 'seq_diagram1.svg'
    #/Users/ehaas/Documents/Python/Flask_Test/static/images/seq_diagram.svg
    return render_template('template.html', my_string=my_string,
        title="Index", current_time=datetime.datetime.now(),
        svg = path.read_text())

@app.route("/discovery")
def discovery():
    my_string="**The Client Searched for User Facing Patient Lists by ... <br>Click on the blue buttons below to continue...**"
    path = Path.cwd() / 'static' / 'images' / 'seq_diagram2.svg'
    #/Users/ehaas/Documents/Python/Flask_Test/static/images/seq_diagram.svg
    return render_template('template.html', my_string=my_string,
        title="Discovery", current_time=datetime.datetime.now(),
        svg = path.read_text())


@app.route("/fetch")
def fetch():
    my_string='''
**After Fetching the List of User Facing lists, a Patient list is selected using a simple Fetch operation: <br>Click on the blue buttons below to continue...

**After Fetching the Patient List, The User wants to get additional Patient data: <br>Click on the blue buttons below to continue...**'''
    path = Path.cwd() / 'static' / 'images' / 'seq_diagram3.svg'
    #/Users/ehaas/Documents/Python/Flask_Test/static/images/seq_diagram.svg
    return render_template('template.html', my_string=my_string,
        title="Discovery", current_time=datetime.datetime.now(),
        svg = path.read_text(),
        )

@app.route("/fetch-more")
def fetch_more():
    my_string="**The User Get additional Patient data one of three ways: <br>Click on the blue buttons below to continue...**"
    #/Users/ehaas/Documents/Python/Flask_Test/static/images/seq_diagram.svg
    return render_template('template.html', my_string=my_string,
        title="Discovery", current_time=datetime.datetime.now(),
        svg = "",
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

if __name__ == '__main__':
    app.run(debug=True)
    app.run(debug=True)
