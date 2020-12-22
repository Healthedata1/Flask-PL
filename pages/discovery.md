The Client Searches for User Facing Patient Lists from an EHR by Querying the *Group* Endpoint...



### Step 1: choose Server Endpoint

{% include "servers.html" %}

**Note**:, all of these scenarios below assume that the server supports, and the client specifies, the `_summary` search parameter in queries for patient list Groups from the server and implements as discussed:

 For Patient List `_summary` require that Servers Shall return all the Group summary elements  + Group.characteristic element
(Based on summary behavior in base specification)

### Step 2: Fetch User Facing lists
There are three ways to do this as described below

#### 1.1 Basic Discovery all User Facing Lists
A server is able to produce a list of the available Patient Lists known.  A client is able to render a list of known Patient Lists.

Action: A client issues a GET request to a server:

       `GET Group?_summary=true&type=person`

Server Success Criteria: The server responds with a complete Bundle of the available Group entries with type person.

Client Success Criteria: The list of lists is processed e.g.,displayed in HTML.

<a href="/fetch-lists?value=all" class="btn btn-primary btn-lg active" role="button" aria-pressed="true">Click Here to Fetch <i>All</i> User Facing Lists</a>

#### 1.2 - Organization-Managed Lists

A server is able to provide a collection of patient lists that are managed by a particular organization.  A client is able to query for lists, specifying the managing Organization in the request.

Action: A client issues a GET request to a server:

       `GET Group?_summary=true&type=person&managingEntity=Organization/42`

Server Success Criteria: The server responds with a Bundle of Group entries where each entry is managed by an Organization with an ID of '42'.

Client Success Criteria: The client provides a selector listing available Organizations.  When selected, a query returns the patient lists that are managed by the selected Organization.

{% with form_action="/fetch-lists", input_id="organization_id", label = "Enter Organization id:", input_name="organization_id", init_value='43', submit_text="Click Here to Fetch All User Facing Lists by Organization" %}
{% include "input_form.html" %}
{% endwith %}

#### 1.3 - Discovery by Group Characteristic

A server is able to provide a collection of patient lists that all have a common characteristic.  A client is able to query for lists, specifying one of the following characteristic parameters in the request:

<table border="black">
<thead>
<tr>
<th>Characteristic</th>
<th>code</th>
<th>Characteristic Value</th>
<th>Value</th>
</tr>
</thead>
<tbody><tr>
<td>characteristic</td>
<td>location</td>
<td>value-reference</td>
<td>Location/[location_id]</td>
</tr>
<tr>
<td>characteristic</td>
<td>practitioner</td>
<td>value-reference</td>
<td>Practitioner/[practitioner_id]</td>
</tr>
<tr>
<td>characteristic</td>
<td>organization</td>
<td>value-reference</td>
<td>Organization/[organization_id]</td>
</tr>
<tr>
<td>characteristic</td>
<td>team</td>
<td>value-reference</td>
<td>CareTeam/[careteam_id]</td>
</tr>
</tbody></table>

This code-system is formally defined [here](https://healthedata1.github.io/Sushi-Sandbox/CodeSystem-argo-group-characteristic.html):
and the value-reference is a custom SearchParameter formally defined [here](https://healthedata1.github.io/Sushi-Sandbox/SearchParameter-Group-value-reference.html):

Action: A client issues a GET request to a server:

       `GET Group?_summary=true&type=person&characteristic=[Code value]&value-reference=[Value value]`

Server Success Criteria: The server responds with a Bundle of Group entries where each entry has the same characteristic code/value pair  (e.g.,  location=Location/[location_id])

Client Success Criteria: The client provides a selector listing above characteristic name-value pairs.  When selected, a query returns the patient lists that are managed by the selected Organization.

{% include "characteristic_list.html" %}
