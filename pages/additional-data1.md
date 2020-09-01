### 3  Getting Extra Details about the patients members in the list

#### 3.1 - Patient Lists - Extra Details via Base FHIR RESTful API Search
The Simplest approach for the client to do a series of queries on the Server to Fetch additional data:

When requested, a server can provides patient details for each for each of the members in the Group resource via a series of FHIR RESTful queries for other resources about that patient as described in the base specification and US Core.

Action: A client issues a GET request, fetching a Group resource.  Then, for each Group.member (aka patient), and Patient resource and a Observation attribute (the most recent lab result) is requested, which is not directly part of the patient resource.

~~~
GET Group/123
for each patient in Group:
GET Patient/ID
GET Observation/$lastn?patient=Patient/ID&category=laboratory
~~~

<button type="button" class="btn btn-primary">Click on Patient to Fetch addtional data...</button>

#### MY Patients:

---
