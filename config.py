from os import path
import os

### paths ###

ENV_PATH = path.join(r"C:\Users\UserX\.conda\envs\opencs_paperclassification")
BASE_DIR = path.join(r"C:\Users\UserX\Desktop\opencs_paperclassification")
ONTOLOGY_DIR = path.join(f"{os.getcwd()}/OpenCS")

DATA_DIR = path.join(BASE_DIR, "data")
RESULT_DIR = path.join(BASE_DIR, "results")
ORIGINAL_FILES_RESULT_DIR = path.join(RESULT_DIR, "results")
QUERY_RESULTS_DIR = path.join(RESULT_DIR, "query_results")
ONTOLOGY_CORE_DIR = path.join(ONTOLOGY_DIR, r"ontology/core")

##############

### URIs ###
TITLE_URI = "http://purl.org/dc/terms/title"
ABSTRACT_URI = "http://purl.org/spar/datacite/hasDescription"
HAS_DISCIPLINE_URI = "http://purl.org/spar/fabio/hasDiscipline"
OCS_URI = "https://w3id.org/ocs/ont/"
PAPER_TYPE_URI = "https://makg.org/class/Paper"

##############

### Elastic Search index ###
IDX_NAME = "ontology_index"

# Elastic Search port
ES_PORT = "9200"
#############
