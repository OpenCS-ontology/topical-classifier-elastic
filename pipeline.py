import time
import os
import json
from rdflib import Graph, URIRef, BNode, Namespace, Literal, XSD
from kneed import KneeLocator

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def extract_title_from_graph(graph: Graph):
    pred_uri = URIRef("http://purl.org/dc/terms/title")
    triples = graph.triples((None, pred_uri, None))
    assert triples
    title_triple = list(triples)[0]
    object_literal = str(title_triple[2])
    return object_literal


def extract_abstract_from_graph(graph: Graph):
    description_uri = URIRef("http://purl.org/spar/datacite/hasDescription")
    node = graph.triples((None, description_uri, None))
    assert node
    abstract_node = list(node)[0][2]
    abstract = list(graph.triples((BNode(abstract_node), None, None)))[1][2]
    return str(abstract)


def extract_embedding_from_graph(graph: Graph):
    bn = Namespace("https://w3id.org/ocs/ont/papers/")
    graph.bind("", bn)
    _emb = graph.triples((None, bn.hasWordEmbedding, None))
    assert _emb
    embedding = eval(str(list(_emb)[0][2]))
    return embedding


def store_records_bulk(es_object, index, data):
    requests = []
    for i, row in enumerate(data):
        request = row
        request["_op_type"] = "index"
        request["_index"] = index
        requests.append(request)
    assert len(requests) > 0
    bulk(es_object, requests)


def find_n_best(result, n, label_colname):
    assert len(result["hits"]["hits"]) >= n
    results = []
    for i in range(n):
        results.append(
            {
                label_colname: result["hits"]["hits"][i]["_source"][label_colname],
                "score": result["hits"]["hits"][i]["_score"],
            }
        )
    return results


def connect_elasticsearch(es_config):
    _es = None
    _es = Elasticsearch([es_config])
    while not _es.ping():
        print("Could not connect to Elastic Search, retrying in 3s...")
        time.sleep(3)
    return _es


def create_concept_json(concept_json_dir):
    concepts = []
    for file_path in os.listdir(concept_json_dir):
        print(f"Indexing {file_path} file...")
        with open(os.path.join(concept_json_dir, file_path), "r") as file:
            concepts_batch = json.load(file)
        for key, value in concepts_batch.items():
            prefLabel = value.get("prefLabel", None)
            broader = value.get("broader", None)
            related = value.get("related", None)
            embedding = value.get("embedding", None)
            concept = {
                "prefLabel": prefLabel if prefLabel else [],
                "broader": broader if broader else [],
                "related": related if related else [],
                "embedding": embedding if embedding else [],
                "opencs_uid": key if key else [],
            }
            concepts.append(concept)
    assert len(concepts) > 0
    return concepts


def get_query(title, abstract, embedding):
    query = {
        "size": 20,
        "query": {
            "bool": {
                "should": [
                    {
                        "function_score": {
                            "query": {
                                "dis_max": {
                                    "queries": [
                                        {
                                            "multi_match": {
                                                "query": title,
                                                "type": "most_fields",
                                                "analyzer": "standard",
                                                "fields": [
                                                    "prefLabel^3",
                                                    "related",
                                                    "broader",
                                                ],
                                                "tie_breaker": 0.5,
                                            }
                                        },
                                        {
                                            "multi_match": {
                                                "query": abstract,
                                                "type": "most_fields",
                                                "analyzer": "standard",
                                                "fields": [
                                                    "prefLabel^3",
                                                    "related",
                                                    "broader",
                                                ],
                                                "tie_breaker": 0.5,
                                            }
                                        },
                                    ]
                                }
                            },
                            "boost": 0.1,
                        }
                    },
                    {
                        "function_score": {
                            "query": {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'embedding')*500",
                                        "params": {"query_vector": embedding},
                                    },
                                }
                            },
                            "boost": 1,
                        }
                    },
                ]
            }
        },
    }
    return query


def add_best_results_to_graph(best_results, file_graph):
    ocs = Namespace("https://w3id.org/ocs/ont/")
    fabio = Namespace("http://purl.org/spar/fabio/")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    base = Namespace("https://w3id.org/ocs/ont/papers/")
    file_graph.bind("ocs", ocs)
    paper_uid = file_graph.value(predicate=rdf.type, object=fabio.ResearchPaper)
    for result in best_results:
        bnode = BNode()
        result_uid = result["opencs_uid"]
        result_score = result["score"]
        file_graph.add((paper_uid, base.hasRelatedTopics, bnode))
        file_graph.add((bnode, base.hasOpencsUID, ocs[result_uid]))
        file_graph.add(
            (bnode, base.relationScore, Literal(result_score, datatype=XSD.integer))
        )
    return file_graph


def main():
    try:
        index_name = "opencs_keywords_index"

        mappings = {
            "mappings": {
                "properties": {
                    "prefLabel": {"type": "text"},
                    "broader": {"type": "text"},
                    "related": {"type": "text"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 768,
                    },
                    "opencs_uid": {"type": "text"},
                }
            }
        }
        with connect_elasticsearch(
            {"host": "localhost", "port": 9200, "scheme": "http"}
        ) as es:
            print(f"Creating index {index_name}...")
            try:
                es.indices.create(index=index_name, body=mappings)
                print("Index created")
                concept_json_dir = "/home/concepts_json"
                concepts = create_concept_json(concept_json_dir)
                store_records_bulk(es, index_name, concepts)
            except:
                print(f"Index {index_name} already exists!")
            archives = ["csis", "scpe"]
            input_path = f"{os.getcwd()}/output"
            for archive in archives:
                root_dir = os.path.join(input_path, archive)
                for dir in os.listdir(root_dir):
                    dir_path = os.path.join(root_dir, dir)
                    for ttl_file in os.listdir(dir_path):
                        print(f"Finding best matching concepts for file {ttl_file}")
                        graph = Graph()
                        ttl_full_path = os.path.join(dir_path, ttl_file)
                        graph.parse(ttl_full_path)
                        file_title = extract_title_from_graph(graph)
                        file_abstract = extract_abstract_from_graph(graph)
                        file_abstract_embedding = extract_embedding_from_graph(graph)
                        query = get_query(
                            file_title, file_abstract, file_abstract_embedding
                        )
                        results = es.search(index=index_name, body=query)
                        assert results
                        n = 20
                        best_n_results = find_n_best(results, n, "opencs_uid")
                        x = [i for i in range(n)]
                        y = [concept["score"] for concept in best_n_results]
                        kl = KneeLocator(
                            x, y, curve="convex", direction="decreasing", online=False
                        )
                        knee = kl.knee
                        result_graph = add_best_results_to_graph(
                            best_n_results[:knee], graph
                        )
                        result_graph.serialize(destination=ttl_full_path)

    except:
        raise


if __name__ == "__main__":
    main()
