import requests
import time
import click
import os
import json

# config
from config import IDX_NAME, ES_PORT
from config import ONTOLOGY_CORE_DIR

from source.ontology_parsing.graph_utils import get_concepts_pref_labels
from source.ontology_parsing.data_loading import (
    get_all_concept_file_paths,
    get_graphs_from_files,
)

from source.result_saving.handle_input_files import classify_input_files
from source.es_index.create_index import build_index
from source.es_index.IndexBaseline import IndexBaseline
from source.env_setup.setup import connect_elasticsearch

from source.data.input_data_reading import get_all_input_file_paths
from source.ontology_parsing.graph_utils import get_uri_to_colname_dict_from_ontology


# to make sure our ES host is responding before an attempt to create an index
def wait_for_localhost_to_response():
    while True:
        try:
            requests.get(f"http://localhost:{ES_PORT}")
            print("ES container is runnng")
            return
        except requests.exceptions.ConnectionError:
            print(
                f"The ES host (http://localhost:{ES_PORT}) is still not responding. Waiting..."
            )
            time.sleep(1)


@click.command()
@click.option(
    "--move_original_files",
    help="Should original input files be deleted from the input directory after classification.",
    metavar="BOOL",
    default=True,
    show_default=True,
)
@click.option(
    "--ask_to_override",
    help="Ask to accept ([y/n]) the result before saving it.",
    metavar="BOOL",
    default=False,
    show_default=True,
)
@click.option(
    "--n", help="Print n best results.", metavar="INT", default=5, show_default=True
)
def main(move_original_files, ask_to_override, n):
    try:
        # creating a dictionary with concepts and their preferred labels
        with open("/home/output_concepts_json", "r") as file:
            labels_to_concepts_names = json.load(file)

        # getting all possible predicates from the ontology
        pred_uri_to_idx_colname = {
            "http://www.w3.org/2004/02/skos/core#closeMatch": "closeMatch",
            "http://www.w3.org/2004/02/skos/core#related": "related",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "type",
            "http://www.w3.org/2004/02/skos/core#broader": "broader",
            "http://www.w3.org/2004/02/skos/core#prefLabel": "prefLabel",
        }

        mappings = {
            "properties": {
                "title": {"type": "text", "analyzer": "english"},
                "ethnicity": {"type": "text", "analyzer": "standard"},
                "director": {"type": "text", "analyzer": "standard"},
                "cast": {"type": "text", "analyzer": "standard"},
                "genre": {"type": "text", "analyzer": "standard"},
                "plot": {"type": "text", "analyzer": "english"},
                "year": {"type": "integer"},
                "wiki_page": {"type": "keyword"},
            }
        }

        es.indices.create(index="movies", mappings=mappings)

        # building a baseline index with all predicates from the ontology
        index_builder = IndexBaseline(
            pred_uri_to_idx_colname, graphs, include_concept_type=True
        )
        wait_for_localhost_to_response()

        build_index(
            index_builder,
            es_config={"host": "localhost", "port": int(ES_PORT), "scheme": "http"},
            idx_name=IDX_NAME,
        )

        archives = ["csis", "scpe"]
        input_path = f"{os.getcwd()}/output"
        for archive in archives:
            root_dir = os.path.join(input_path, archive)
            for dir in os.listdir(root_dir):
                dir_path = os.path.join(root_dir, dir)
                print(
                    f"Reading all input files with articles to be classified from: {dir_path}"
                )
                input_files_paths = get_all_input_file_paths(dir_path)

                with connect_elasticsearch(
                    {"host": "localhost", "port": ES_PORT, "scheme": "http"}
                ) as es:
                    classify_input_files(
                        input_files_paths,
                        labels_to_concepts_names,
                        es,
                        IDX_NAME,
                        n=n,
                        move_original=False,
                        ask_to_override=False,
                    )

        print("End. Check the results dir.")
    except:
        raise


if __name__ == "__main__":
    main()
