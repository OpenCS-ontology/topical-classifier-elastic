import os
import copy
from typing import List, Dict
from elasticsearch import Elasticsearch
from rdflib import Graph, URIRef

from config import (
    TITLE_URI,
    ABSTRACT_URI,
    HAS_DISCIPLINE_URI,
    OCS_URI,
    PAPER_TYPE_URI,
    ORIGINAL_FILES_RESULT_DIR,
)
from source.data.input_data_reading import (
    input_file_to_graph,
    extract_title_from_graph,
    extract_abstract_from_graph,
    extract_embedding_from_graph,
)
from source.es_index.query_index import find_n_best
from source.result_saving.result_vocabulary import save_result_vocabulary


title_placeholder = "#ARTICLE_TITLE"
abstract_placeholder = "#ARTICLE_ABSTRACT"


def get_query(title, abstract, embedding):
    query = {
        "query": {
            "dis_max": {
                "queries": [
                    {
                        "multi_match": {
                            "query": title,  # PLACEHOLDER for an article title value (the same query for all files)
                            "type": "most_fields",
                            "analyzer": "standard",
                            "fields": ["prefLabel^3", "related", "broader"],
                            "tie_breaker": 0.5,
                        }
                    },
                    {
                        "multi_match": {
                            "query": abstract,  # PLACEHOLDER for an article abstract value (the same query for all files)
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


def classify_input_files(
    input_files_paths: List[str],
    labels_to_concept_names: Dict[str, str],
    es: Elasticsearch,
    index_name: str,
    n: int,
    label_colname: str = "prefLabel",
    ask_to_override: bool = False,
    move_original: bool = True,
):
    query_results = []
    n_files = len(input_files_paths)
    for i in range(n_files):
        input_file_path = input_files_paths[i]
        file_name, file_format = _get_file_name_format(input_file_path)
        print("###")
        print(f"Parsing a next file {i + 1}/{n_files}: ")
        title, abstract, embedding = _parse_input_file(
            input_file_path, TITLE_URI, ABSTRACT_URI, file_format
        )
        _query = get_query(title=title, abstract=abstract, embedding=embedding)
        # _replace_title_abstract_placeholders(
        #     _query, title, abstract, title_placeholder, abstract_placeholder
        # )

        query_result = find_n_best(es, index_name, _query, n)
        print(f"Query result for a file {file_name}:")
        print(query_result)

        # if _decide_to_override(ask_to_override):
        #     continue
        # print("Saving the result and updating the discipline with the best result.")

        # best_concept, _ = _get_best_concept_and_score(
        #     query_result, labels_to_concept_names, label_colname
        # )
        # _override_and_move_input_file(
        #     input_file_path, best_concept, move_original, file_format
        # )
        # save_result_vocabulary(_query, query_result, file_name)
        # query_results.append(query_result)

    return query_results


def _get_file_name_format(input_file_path: str):
    file_name, ext = os.path.splitext(input_file_path)
    file_name = os.path.basename(file_name)
    return file_name, ext.split(".")[1]


def _parse_input_file(
    input_file_path: str, title_uri: str, abstract_uri: str, file_format: str
):
    graph = input_file_to_graph(input_file_path, file_format)
    title = extract_title_from_graph(graph, title_uri)
    print(f"Processing file: {title}...")
    abstract = extract_abstract_from_graph(graph, abstract_uri)
    embedding = extract_embedding_from_graph(graph)
    return title, abstract, embedding


def _decide_to_override(ask_to_override: bool):
    if not ask_to_override:
        return False
    x = input(
        "Should we accept the best result and override the input file's discipline [y/n]?"
    )
    return x != None and x.strip().lower() == "y"


def _override_and_move_input_file(
    input_file_path, best_concept: str, move_original: bool, file_format: str = ".ttl"
):
    graph = input_file_to_graph(input_file_path)
    graph.bind("ocs", OCS_URI)

    paper_URI = list(
        graph.triples(
            (
                None,
                URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                URIRef(PAPER_TYPE_URI),
            )
        )
    )[0][0]
    has_discipline_URI = URIRef(HAS_DISCIPLINE_URI)
    best_concept_URI = URIRef(OCS_URI + best_concept)

    _update_has_discipline_result(
        graph, paper_URI, has_discipline_URI, best_concept_URI
    )

    _move_updated_file(graph, input_file_path, move_original, file_format)


def _update_has_discipline_result(
    graph: Graph,
    paper_URI: URIRef,
    has_discipline_URI: URIRef,
    best_concept_URI: URIRef,
):
    if (paper_URI, has_discipline_URI, None) in graph:
        graph.remove((paper_URI, has_discipline_URI, None))
    graph.add((paper_URI, has_discipline_URI, best_concept_URI))


def _move_updated_file(
    graph: Graph, input_file_path: str, move_original: bool, file_format: str = "ttl"
):
    if move_original and os.path.isfile(input_file_path):
        os.remove(input_file_path)

    file_name = os.path.basename(input_file_path)

    output_file_path = os.path.join(ORIGINAL_FILES_RESULT_DIR, file_name)
    graph.serialize(output_file_path, file_format)


def _get_best_concept_and_score(
    query_result: str, labels_to_concepts_names: Dict[str, str], label_colname: str
):
    best_concept_label = query_result[0][label_colname][0]
    best_concept_score = query_result[0]["score"]

    if "C1" in labels_to_concepts_names:
        labels_to_concepts_names = {v: k for k, v in labels_to_concepts_names.items()}
    best_concept = labels_to_concepts_names[best_concept_label]
    return best_concept, best_concept_score


# def _replace_title_abstract_placeholders(
#     val, title_val, abstract_val, title_placeholder, abstract_placeholder
# ):
#     if type(val) == dict:
#         dictionary = val
#         for k, v in dictionary.items():
#             if type(v) != str:
#                 _replace_title_abstract_placeholders(
#                     v, title_val, abstract_val, title_placeholder, abstract_placeholder
#                 )
#             else:
#                 if title_placeholder in v:
#                     dictionary[k] = v.replace(title_placeholder, title_val)

#                 if abstract_placeholder in v:
#                     dictionary[k] = v.replace(abstract_placeholder, abstract_val)

#     elif type(val) == list or type(val) == tuple:
#         for v in val:
#             _replace_title_abstract_placeholders(
#                 v, title_val, abstract_val, title_placeholder, abstract_placeholder
#             )
