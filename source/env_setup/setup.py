from config import *
from typing import List, Dict
from elasticsearch import Elasticsearch


def connect_elasticsearch(
    es_config: Dict[str, str] = {"host": "localhost", "port": 9200, "scheme": "http"}
):
    _es = None
    _es = Elasticsearch([es_config])
    if _es.ping():
        print("Yay Connected")
    else:
        print("Awww it could not connect!")
    return _es
