**This is a simple python Flask App FHIR Facade which:**

- [X] use same Flask app framework as notifications
    - [X] set up pages
        - [X] home, contacts etc
        - [X] steps 1,2,3
        - [X] display
        - [ ] TODO validate
    - [X] update figures etc

**NEXT STEPS:**

- [ ] Complete Get additional patient data by
    - [ ] get Observation
    - [X] multipleOr
    - [X] Batch
    - [X] _include
    - [X] Q/QR
          - [X] create sample Q and generate QA from them
                - [ ] TODO update to use DateTime and other types in addition to String
          - [X] define extensions
    - [ ] add in Encounter and Appointment Extension Querying Examples
- [X] set up test data using notifications data set
    - [X] create Groups from data - using managing entity and provider characteristic to start
    - [X] start on HAPI Test Server
      - Zulip to support query QR by questionnaire parameter
- [ ] since server's won't support support custom SP or QM extensions
    - [X] need to simulate using this as facade
- [ ] TODO use AIDBox or FHIRBase

The source code can be found on *github*: <https://github.com/Healthedata1/PL-Client>

This application is deployed on [![pythonanywhere](https://www.pythonanywhere.com/static/anywhere/images/PA-logo.svg)](https://www.pythonanywhere.com/)
