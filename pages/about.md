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
    - [ ] Q/QR
          - [ ] create sample Q and generate QA from them
                - [ ] TODO figure out how - SDC extensions?
          - [ ] define extensions
- [ ] set up test data using notifications data set
    - [ ] create Groups from data - using managing entity and provider characteristic to start
    - [ ] start on HAPI
- [ ] since server's won't support support custom SP or QM extensions
    - [X] need to simulate using this as facade
    - [ ] TODO use GRAPHQL if supported else

- [ ] TODO use HealthSamuri

The source code can be found on *github*: <https://github.com/Healthedata1/PL-Client>

This application is deployed on [![pythonanywhere](https://www.pythonanywhere.com/static/anywhere/images/PA-logo.svg)](https://www.pythonanywhere.com/)
