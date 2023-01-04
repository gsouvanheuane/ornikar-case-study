# ornikar-case-study
Developed by Gaëlle Souvanheuane, 05-01-2023

## Installation
Please run the following command:

``virtualenv .venv && source .venv/bin/activate && pip install -r requirements.txt``

## Pre-requirements
You need to add a `.env` file at the root and set it up as follow:
````
GOOGLE_APPLICATION_CREDENTIALS= path/to/secrets.json
````
The variable `GOOGLE_APPLICATION_CREDENTIALS` should be the path to the json file which contains the credentials to connect to the BigQuery database
## Usage
You will find all answers of the case study in `src/`
- To run question 1a: ` python -m src.question1a `
- To run question 1b: `python -m src.question1b`
  - Run Unitary Tests: `pytest -v tests/`
