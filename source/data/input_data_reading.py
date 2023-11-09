from rdflib import Graph, URIRef, BNode, Namespace
import glob
from os import path
from typing import List


def get_all_input_file_paths(input_data_dir: str, files_format="ttl") -> List[str]:
    files = glob.glob(path.join(input_data_dir, f"*.{files_format}"))
    return files


def input_file_to_graph(input_file_path: str, file_format: str = "ttl"):
    graph = Graph()
    graph.parse(input_file_path, file_format)
    return graph


def extract_title_from_graph(graph: Graph, predicate_uri: str):
    pred_uri = URIRef(predicate_uri)
    title_triple = list(graph.triples((None, pred_uri, None)))[0]
    object_literal = str(title_triple[2])
    return object_literal


def extract_abstract_from_graph(graph: Graph, predicate_uri: str):
    description_uri = URIRef(predicate_uri)
    abstract_node = list(graph.triples((None, description_uri, None)))[0][2]
    abstract = list(graph.triples((BNode(abstract_node), None, None)))[1][2]
    return abstract


def extract_embedding_from_graph(graph: Graph):
    bn = Namespace("https://w3id.org/ocs/ont/papers/")
    graph.bind("", bn)
    embedding = eval(str(list(graph.triples((None, bn.hasWordEmbedding, None)))[0][2]))
    return embedding
