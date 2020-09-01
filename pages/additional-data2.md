

Server Success Criteria: The client bundles the Observation GET requests in a request Bundle, sending a minimum number of GET requests to the server.

The server responds with a search Bundle for each query.

Client Success Criteria: The request bundle is properly prepared, minimizing GET operations against the server.  All fetched 'extra details' are then also processes them e.g.,displayed in HTML.

>Discussion 1) These queries can be combined using the OR search parameter to reduce the number of Client queries.
>
> `GET Patient?_id=ID1,ID2,ID3,...`
> `GET Observation/$lastn?patient=ID1,ID2,ID3,...&category=laboratory`
>
>Server Success Criteria: The client bundles the Observation GET requests in a request Bundle, sending a minimum number of GET requests to the server.
>
>The server responds with a search Bundle for each query.
>
>Client Success Criteria: The request bundle is properly prepared, minimizing GET operations against the server.  All fetched 'extra details' are then also processes them e.g.,displayed in HTML.
>
>Note that US Core does not require servers to support multipleOr for these queries
>
>Should this be part of the basic Patient list API - e.g., Servers SHALL/SHOULD/MAY Support?

> Discussion 2) These queries can be done separately as described above or as a single batch interaction
>
`POST [base]`

~~~JSON
{
  "resourceType": "Bundle",
  "id": "bundle-request-groupdetails",
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

>Should this be part of the basic Patient list API - e.g., Servers SHALL/SHOULD/MAY Support?
>
>Server Success Criteria: The client bundles the Observation GET requests in a request Bundle, sending a minimum number of GET requests to the server.
>
>The server SHALL return a Bundle with type set to batch-response that contains the request resource for each entry in the  batch request, in the same order, with the outcome of processing the entry.
>
>Client Success Criteria: The request bundle is properly prepared, minimizing GET operations against the server.  All fetched 'extra details' are then also processes them e.g.,displayed in HTML.


#### 3.2 - Using _include:
Support _include for Group so that the Patient resource attributes such as Name, Age, DOB, Gender, Height, Weight, etc can be fetched in a single interaction (this is functionally akin to using the `_list` parameter)

`GET [base]/Group/1234&_include=Group:member`

Server Success Criteria: The server responds with a complete Bundle of Patient entries, all members of the requested Group with ID '123' AND a Patient resource for each Group.member.

Client Success Criteria: The client queries for a particular list of patients and processes them e.g.,displayed in HTML as a table of patient resource attributes such as Name, Age, DOB, Gender, MRN, Contact info.

>Discussion: Should this be part of the basic Patient list API - e.g., Servers SHALL/SHOULD/MAY Support?


#### 3.3 - Patient Lists - Extra Details via Questionnaire

See full example of this exchange: https://hackmd.io/AfJ9YNb6TNGeDSuAaHIn1g?view#Patients-with-column-data

When requested, a server provides patient details that are not present in the patient resource directly via a Questionnaire and QuestionnaireResponse as follows:

A client issues a GET request, fetching a patient list (aka Group resource).  The Group resource has an extension that references a Questionnaire url which defines the extra data to be returned for that group of patients and a second extension for each Patient entry in the Group referencing a QuestionnaireResponse resource containing the patient-level data. (See example extension).
The server is able to populate corresponding QuestionnaireResponses with the appropriate data for each patient.
 Then, for each patient in the list, the client may fetch the QuestionnaireResponse for the above Questionnaire.
        GET Group/123

Server Success Criteria:  The server responds with a  Group resource with ID '123' that has the two extensions: a Questionnaire resource and a QuestionnaireResponse resource for each patient.

Client Success Criteria: The client queries for a particular list of patients.  The Client make All extra patient details are extracted from a QuestionnaireResponse resource.

**Option 1:**

for each patient in group123.bundle.entry get QR:  GET QuestionnaireResponse/[QuestionnaireResponse resource id from Group.member.entity.extension]

**Option 2:**  Get all QR for groups based on Q url

GET QuestionnaireResponse?q=/[Questionnaire url from Group.extension]


Server Success Criteria:  The server responds with search Bundle with each entry a QuestionnaireResponse resources for each patient containing the requested patient attributes.

Client Success Criteria:  The Client extracts the extra patient details from the QuestionnaireResponse resources and processes them e.g., populates a table for display.

> Discussion:

> 1. identify how the appropriate questionnaire is determined for a group or particular context.

> 2. This information could easily be transmitted as a binary (csv)  or in the
Group.member.display element as a delimited string. Is the added complexity
worth it and what are the real benefits here?
