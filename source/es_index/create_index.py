from typing import Dict
from source.es_index.IIndexBuilder import IIndexBuilder
import requests
import json
from source.env_setup.setup import connect_elasticsearch
from elasticsearch.helpers import bulk
from config import ES_PORT


def store_record(es_object, index, data):
    is_stored = True

    try:
        outcome = es_object.index(index=index, doc_type="_doc", body=json.dumps(data))
        print(outcome)
    except Exception as ex:
        print("Error in indexing data")
        print(str(ex))
        is_stored = False
    finally:
        return is_stored


def store_records_bulk(es_object, index, data):
    requests = []
    for i, row in enumerate(data):
        request = row
        request["_op_type"] = "index"
        request["_index"] = index
        requests.append(request)
    bulk(es_object, requests)


def build_index(
    index_builder: IIndexBuilder,
    es_config: Dict[str, str] = {
        "host": "localhost",
        "port": ES_PORT,
        "scheme": "http",
    },
    idx_name: str = "ontology",
):
    template = index_builder.get_template()
    create_index(str(template), es_config, idx_name)
    rows = index_builder.build_rows()

    es = connect_elasticsearch(es_config)
    store_records_bulk(es, idx_name, rows)
    es.close()
    # try:
    #     template = index_builder.get_template()
    #     create_index(str(template), es_config, idx_name)
    #     rows = index_builder.build_rows()

    #     es = connect_elasticsearch(es_config)
    #     store_records_bulk(es, idx_name, rows)

    #     # for row in rows:
    #     #    store_record(es, idx_name, row)

    # except Exception as e:
    #     print(str(e))
    # finally:
    #     es.close()


def create_index(
    template: str,
    es_config: Dict[str, str] = {"host": "localhost", "port": 9200},
    idx_name: str = "ontology",
):
    template = template.replace("'", '"')
    query = json.loads(template)
    response = requests.put(
        f'http://{es_config["host"]}:{es_config["port"]}/{idx_name}', json=query
    )
    response.json()
