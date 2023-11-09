import requests
import time
import click
import os
import json
from rdflib import Graph, URIRef, BNode, Namespace

from elasticsearch import Elasticsearch


def extract_title_from_graph(graph: Graph):
    pred_uri = URIRef("http://purl.org/dc/terms/title")
    title_triple = list(graph.triples((None, pred_uri, None)))[0]
    object_literal = str(title_triple[2])
    return object_literal


def extract_abstract_from_graph(graph: Graph):
    description_uri = URIRef("http://purl.org/spar/datacite/hasDescription")
    abstract_node = list(graph.triples((None, description_uri, None)))[0][2]
    abstract = list(graph.triples((BNode(abstract_node), None, None)))[1][2]
    return abstract


def extract_embedding_from_graph(graph: Graph):
    bn = Namespace("https://w3id.org/ocs/ont/papers/")
    graph.bind("", bn)
    embedding = eval(str(list(graph.triples((None, bn.hasWordEmbedding, None)))[0][2]))
    return embedding


def get_query(title, abstract, embedding):
    query = {
        "query": {
            "dis_max": {
                "queries": [
                    {
                        "multi_match": {
                            "query": title,
                            "type": "most_fields",
                            "analyzer": "standard",
                            "fields": ["prefLabel^3", "related", "broader"],
                            "tie_breaker": 0.5,
                        }
                    },
                    {
                        "multi_match": {
                            "query": abstract,
                            "type": "most_fields",
                            "analyzer": "standard",
                            "fields": ["prefLabel^3", "related", "broader"],
                            "tie_breaker": 0.5,
                        }
                    },
                ]
            }
        }
    }
    return query


def main():
    try:
        index_name = "opencs_keywords_index"

        mappings = {
            "mappings": {
                "properties": {
                    "prefLabel": {"type": "keyword"},
                    "broader": {"type": "keyword"},
                    "related": {"type": "keyword"},
                    "embedding": {"type": "float"},
                }
            }
        }
        with Elasticsearch(
            [{"host": "localhost", "port": 9200, "scheme": "http"}]
        ) as es:
            es.indices.create(index=index_name, body=mappings)

        for file in os.listdir("/home/concepts.json"):
            print(f"Indexing {file} file...")
            concepts_batch = json.load(file)
            for key, value in concepts_batch.items():
                concept = {
                    "prefLabel": value["prefLabel"],
                    "related": value["related"],
                    "broader": value["broader"],
                    "embedding": value["embedding"],
                }
                es.index(index=index_name, id=key, body=concept)

        archives = ["csis", "scpe"]
        input_path = f"{os.getcwd()}/output"
        for archive in archives:
            root_dir = os.path.join(input_path, archive)
            for dir in os.listdir(root_dir):
                dir_path = os.path.join(root_dir, dir)
                for ttl_file in os.listdir(dir_path):
                    print(f"Finding best matching concepts for file {ttl_file}...")
                    graph = Graph()
                    graph.parse(ttl_file)
                    file_title = extract_title_from_graph(graph)
                    file_abstract = extract_abstract_from_graph(graph)
                    file_abstract_embedding = extract_abstract_from_graph(graph)
                    query = get_query(
                        file_title, file_abstract, file_abstract_embedding
                    )
                    results = es.search(index=index_name, body=query)
                    for hit in results["hits"]["hits"]:
                        print(hit["_score"])
                        print(hit["_source"])
                    break

    except:
        raise


if __name__ == "__main__":
    main()
