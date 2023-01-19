from os import path



### paths ###

ENV_PATH = path.join(r"C:\Users\golik\.conda\envs\opencs_paperclassification")
BASE_DIR = path.join(r"C:\Users\golik\Desktop\mgr\semantic\project\opencs_paperclassification")
ONTOLOGY_DIR = path.join(r"D:\OpenCS\OpenCS")

DATA_DIR = path.join(BASE_DIR, "data")
RESULT_DIR = path.join(BASE_DIR, "results")
ONTOLOGY_CORE_DIR = path.join(ONTOLOGY_DIR, r"ontology\core" )

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
