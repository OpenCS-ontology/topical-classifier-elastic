from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, XSD
import uuid
import datetime
from rdflib.namespace import Namespace
from config import QUERY_RESULTS_DIR
from os import path



def save_result_vocabulary(query, query_res, original_file_name=None, save_as_file=True):
    schema = Namespace("http://schema.org/")

    res_uuid = str(uuid.uuid4())
    g = Graph()

    g.bind("ocs", "https://w3id.org/ocs/ont/")
    g.bind("schema", schema)
    g.bind("rdf", RDF)
    g.bind("xsd", XSD)

    res = URIRef(f"http://example.org/result/{res_uuid}")

    query_literal = Literal(query)
    query_res_literal = Literal(query_res)
    end_time_literal = Literal(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), datatype=XSD.date)

    g.add((res, RDF.type, schema.SearchAction))
    g.add((res, schema.query, query_literal))
    g.add((res, schema.result, query_res_literal))
    g.add((res, schema.endTime, end_time_literal))

    if save_as_file:
        file_name = f"{res_uuid}.ttl"
        if original_file_name != None:
            file_name = f"{original_file_name}_{file_name}"
        dest_path = path.join(QUERY_RESULTS_DIR, file_name)
        g.serialize(dest_path, format="turtle")

    return str(g.serialize())
    