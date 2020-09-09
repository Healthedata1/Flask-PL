### The *{{base_name}}* FHIR Server returns a Group resource which contains references to patients in response a client issuing the following FHIR RESTful GET request to the server:

    {{url_string}}

Server Success Criteria: The server responds with a complete Bundle of Patient entries, all members of the requested Group resource with ID '123'.

Client Success Criteria: The client queries for a particular list of patients and processes them e.g.,displayed in HTML as a list of ids:

**CLICK ON THE BLUE BUTTON ABOVE TO FETCH MORE DATA ABOUT THE PATIENTS ON THE LIST**

---
