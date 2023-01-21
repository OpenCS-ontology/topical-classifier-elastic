from rdflib import Graph, URIRef
import glob
from os import path
from typing import List



def get_all_input_file_paths(input_data_dir: str, files_format='ttl') -> List[str]:
    files = glob.glob(path.join(input_data_dir, f'*.{files_format}'))
    return files

def input_file_to_graph(input_file_path: str, file_format: str='ttl'):
    graph = Graph()
    graph.parse(input_file_path, file_format)
    return graph

def extract_object_literal_from_graph(graph: Graph, predicate_uri: str):
    pred_uri=URIRef(predicate_uri)
    title_triple = list(graph.triples((None, pred_uri, None)))[0]
    object_literal = str(title_triple[2])
    return object_literal
