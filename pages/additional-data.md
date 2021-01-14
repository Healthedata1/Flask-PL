### 3  Getting Extra Details about the patients members in the list
<a id="endpoint"></a>

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

##### Step 1: Click on Patient to Fetch Additional Data for *Individual* Patient

{% with collapse_id="endpoint" %}{% include "collapse.html" %}{% endwith %}

{% include "mypatients.html" %}

Server Success Criteria: The client bundles the Observation GET requests in a request Bundle, sending a minimum number of GET requests to the server.

The server responds with a search Bundle for each query.

Client Success Criteria: The request bundle is properly prepared, minimizing GET operations against the server.  All fetched 'extra details' are then also processes them e.g.,displayed in HTML.

<a id="multiple_or"></a>
#### 3.1 a) - Patient Lists - Using the multipleOr search parameter

To to reduce the number of queries, the client may use the multipleOr search parameter:

 `GET Patient?_id=ID1,ID2,ID3,...`
 `GET Observation/$lastn?patient=ID1,ID2,ID3,...&category=laboratory`

Server Success Criteria: The client bundles the Observation GET requests in a request Bundle, sending a minimum number of GET requests to the server.

The server responds with a search Bundle for each query.

Client Success Criteria: The request bundle is properly prepared, minimizing GET operations against the server.  All fetched 'extra details' are then also processes them e.g.,displayed in HTML.

<a href="/fetch-more?multipleOr=true" class="btn btn-primary active" role="button" data-toggle="collapse" data-target="#multiple_or" aria-pressed="true">Step 1: Click Here to Fetch Additional Data for *All* Patients Using the multipleOr Functionality</a>

{% with collapse_id="multiple_or" %}{% include "collapse.html" %}{% endwith %}

Note that US Core does not require servers to support multipleOr for these queries

<a id="batch"></a>
#### 3.1 b) - Patient Lists - Using a single batch or transcaction interaction

`POST [base]`

~~~JSON
{
  "resourceType": "Bundle",
  "type": "batch",
  "entry": [
    {
      "request": {
        "method": "GET",
        "url": "Patient/123"
      }
    },
    {
      "request": {
        "method": "GET",
        "url": "/Observation/$lastn?patient=Patient/123&category=laboratory"
      }
    },
    {
      "request": {
        "method": "GET",
        "url": "Patient/456"
      }
    },
    {
      "request": {
        "method": "GET",
        "url": "/Observation/$lastn?patient=Patient/456&category=laboratory"
      }
    },
    ...
  ]
}
~~~

Should this be part of the basic Patient list API - e.g., Servers SHALL/SHOULD/MAY Support?

Server Success Criteria: The client bundles the Observation GET requests in a request Bundle, sending a minimum number of GET requests to the server.

The server SHALL return a Bundle with type set to batch-response that contains the request resource for each entry in the  batch request, in the same order, with the outcome of processing the entry.

Client Success Criteria: The request bundle is properly prepared, minimizing GET operations against the server.  All fetched 'extra details' are then also processes them e.g.,displayed in HTML.
 <a href="/fetch-more?batch=true" class="btn btn-primary active" role="button" aria-pressed="true">Step 1: Click Here to Fetch Additional Data for *All* Patients Using the Batch Functionality</a>

{% with collapse_id="batch" %}{% include "collapse.html" %}{% endwith %}

<a id="include"></a>
#### 3.2 - Using _include:

Support _include for Group so that the Patient resource attributes such as Name, Age, DOB, Gender, Height, Weight, etc can be fetched in a single interaction (this is functionally akin to using the `_list` parameter)

`GET [base]/Group/1234&_include=Group:member`

Server Success Criteria: The server responds with a complete Bundle of Patient entries, all members of the requested Group with ID '123' AND a Patient resource for each Group.member.

Client Success Criteria: The client queries for a particular list of patients and processes them e.g.,displayed in HTML as a table of patient resource attributes such as Name, Age, DOB, Gender, MRN, Contact info.

<a href="/fetch-more?include=true" class="btn btn-primary active" role="button" aria-pressed="true">Step 1: Click Here to Fetch Additional Data for *All* Patients Using the _include Functionality</a>

{% with collapse_id="include" %}{% include "collapse.html" %}{% endwith %}

<a id="qr"></a>
#### 3.3 - Patient Lists - Extra Details via Questionnaire

See full example of this exchange: https://hackmd.io/AfJ9YNb6TNGeDSuAaHIn1g?view#Patients-with-column-data

When requested, a server provides patient details that are not present in the patient resource directly via a Questionnaire and QuestionnaireResponse as follows:

The Questionnaire *defines* the data to be returned for each patient:

<a href="{{session_base}}/{{session_q}}" class="btn btn-primary active" role="button" aria-pressed="true">Click Here to View The Questionnaire</a>

A client issues a GET request, fetching a patient list (aka Group resource).  The Group resource has an extension that references a Questionnaire url which defines the extra data to be returned for that group of patients and a second extension for each Patient entry in the Group referencing a QuestionnaireResponse resource containing the patient-level data. (See example extension).
The server is able to populate corresponding QuestionnaireResponses with the appropriate data for each patient.
 Then, for each patient in the list, the client may fetch the QuestionnaireResponse for the above Questionnaire.
        GET Group/123

Server Success Criteria:  The server responds with a  Group resource with ID '123' that has the two extensions: a Questionnaire resource and a QuestionnaireResponse resource for each patient.

Client Success Criteria: The client queries for a particular list of patients.  The Client make All extra patient details are extracted from a QuestionnaireResponse resource.

#### 3.3 a) Option 1: Get QR for each patient

For each patient in group123.bundle.entry get QR:  GET QuestionnaireResponse/[QuestionnaireResponse resource id from Group.member.entity.extension]

##### Step 1: Click on a Patient below to Fetch Additional Data for *Individual* Patient using Questionnaire and QuestionnaireResponse

{% with collapse_id="qr" %}{% include "collapse.html" %}{% endwith %}

*Note these values have been randomly generated for demonstration purposes*

{% if qr_ext_exist %}

{% include "myqr.html" %}

{% else %}

---
<img alt="NO Q/QR extension for this Group" class="img-responsive project-logo" src="../static/images/empty.png">
 *NO Q/QR extension for this Group*

---

{% endif %}

<a id="qrbonus"></a>
#### 3.3 b) Bonus - Option 2: Get all QR for groups using multipleOr, batch/transaction or based on Q url

See above for multipleOr, batch/transaction

also using the search `questionnaire` search parameter all the QuestionnaireResponses can be fetched in a single query.  *Note that this does not limit to the members in the group*.

GET QuestionnaireResponse?questionnaire=[Questionnaire url from Group.extension]

Server Success Criteria:  The server responds with search Bundle with each entry a QuestionnaireResponse resources for each patient containing the requested patient attributes.

Client Success Criteria:  The Client extracts the extra patient details from the QuestionnaireResponse resources and processes them e.g., populates a table for display.

</figure style="text-align: center;">
<img alt="visit our website" class="img-responsive project-logo" src="../static/images/rabbit-hole.png">
<figcaption>...TODO...</figcaption>
</figure>

<!--
<a href="/todo" type="button" class="btn btn-primary">Click Here to Fetch *All* Additional Data Patients using Questionnaire and QuestionnaireResponse</a>
-->

<a id="appt-enc"></a>
#### 3.4 - NEW Patient Lists - Extra Details Using additional Appointment and/or Encounter extensions

If the Group resource has an extension on each member that references an Appointment or Encounter which is the reason patient on the list, then, for each patient in the list (`Group.member`), the client may fetch the corresponding Appointment or Encounter.

For Example: for each patient in Group/123.bundle.entry get Appointment/123 and Encounter/123

   `GET Appointment/[Appointment resource id from Group.member.entity.extension]`

   `GET Encounter/[Encounter resource id from Group.member.entity.extension]`

   For each patient in group123.bundle.entry get QR:  GET QuestionnaireResponse/[QuestionnaireResponse resource id from Group.member.entity.extension]

Server Success Criteria: The server responds with an Encounter or Appointment resource.

Client Success Criteria: The Client extracts the extra patient details from the resource and processes them e.g., populates a table for display.

---
<a id="appt_ext"></a>
 ##### Step 1: Click on a Patient below to Fetch Additional Appointment Data for *Individual* Patients using the Appointment Extension

 {% with collapse_id="appt_ext" %}{% include "collapse.html" %}{% endwith %}

 *Note these values have been randomly generated for demonstration purposes*

 {% if appt_ext_exist %}

 {% include "my_appt.html" %}

 {% else %}

---
<img alt="NO Appointment extension for this Group" class="img-responsive project-logo" src="../static/images/empty.png">
 *NO Appointment extension for this Group*

---

{% endif %}

---
<a id="enc_ext"></a>
 ##### Step 1: Click on a Patient below to Fetch Additional Encounter Data for *Individual* Patients using the Encounter Extension

 {% with collapse_id="enc_ext" %}{% include "collapse.html" %}{% endwith %}

 *Note these values have been randomly generated for demonstration purposes*

 {% if enc_ext_exist %}

 {% include "my_enc.html" %}

 {% else %}

---
<img alt="NO Encounter extension for this Group" class="img-responsive project-logo" src="../static/images/empty.png">
 *NO Encounter extension for this Group*

---

{% endif %}

---

**Bonus**:   Get all Encounters or Appointments for group.member list

 a )  based on multipleORs or Transaction Bundle

</figure style="text-align: center;">
<img alt="visit our website" class="img-responsive project-logo" src="../static/images/rabbit-hole.png">
<figcaption>...TODO...</figcaption>
</figure>




 Discussion:

> 1. identify how the appropriate questionnaire is determined for a group or particular context.
