from os import path



### paths ###

ENV_PATH = path.join(r"C:\Users\UserX\.conda\envs\opencs_paperclassification")
BASE_DIR = path.join(r"C:\Users\UserX\Desktop\opencs_paperclassification")
ONTOLOGY_DIR = path.join(r"D:\OpenCS\OpenCS")

DATA_DIR = path.join(BASE_DIR, "data")
INPUT_FILES_DIR = path.join(DATA_DIR, r"input_ttl_files/")
RESULT_DIR = path.join(BASE_DIR, "results")
ORIGINAL_FILES_RESULT_DIR = path.join(RESULT_DIR, "results")
QUERY_RESULTS_DIR = path.join(RESULT_DIR, "query_results")
ONTOLOGY_CORE_DIR = path.join(ONTOLOGY_DIR, r"ontology\core" )

##############

### URIs ###
TITLE_URI = "http://purl.org/dc/terms/title"
ABSTRACT_URI = "http://purl.org/dc/terms/abstract"
HAS_DISCIPLINE_URI = "http://purl.org/spar/fabio/hasDiscipline"
OCS_URI = "https://w3id.org/ocs/ont/"
PAPER_TYPE_URI = "https://makg.org/class/Paper"

##############

### docker ###

# docker images
ES_IMAGE = "docker.elastic.co/elasticsearch/elasticsearch:7.12.1"
KB_IMAGE = "docker.elastic.co/kibana/kibana:7.12.1"

# containers
ES_CONTAINER_NAME = "opencs-pc-es"
KB_CONTAINER_NAME = "opencs-pc-kb"

ES_PORTS = {9200:9200, 9300:9300}
KB_PORTS = {5601:5601}

PORT = list(ES_PORTS.keys())[0]

# docker network
NETWORK = 'elastic_net'

##############

### Elastic Search index ###
IDX_NAME = 'ontology_index'


#############
