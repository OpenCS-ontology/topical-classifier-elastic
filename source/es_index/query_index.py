from elasticsearch import Elasticsearch
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from source.env_setup.setup import connect_elasticsearch
from config import IDX_NAME



def _find_n_best(result, n: int, label_colname: str):
    results = []
    for i in range(n):
        results.append(
            {
                label_colname: result["hits"]["hits"][i]["_source"][label_colname],
                "score": result["hits"]["hits"][i]["_score"]
            }
        )
    return results

def find_n_best(es: Elasticsearch, index_name: str, query: str, n: int, label_colname: str='prefLabel'):
    res = es.search(index=index_name, body=query)
    return _find_n_best(res, n, label_colname)


punctuation  = {
    '.' : '',
    ',' : '',
    ':' : '',
    ';' : '',
    '_' : '',
    ' %' : 'percent',
    '%' : ' percent',
    '!' : '',
    '?' : '',
    '/' : ' ',
    '(' : '',
    ')' : '',
    '\'' : '',
    '`' : '',
    '-' : ' ',
    '’' : ''
}


def replace_characters(text, DICT):
    for key, value in DICT.items():
         text = text.replace(key, value)
    return text


def preprocess_text(text):
    text = text.lower()

    text = replace_characters(text, punctuation)

    text_tokens = word_tokenize(text)
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
    return ' '.join(list(set(tokens_without_sw)))


def query_es_title(title):
    title = preprocess_text(title)
    query = {
        "query": {
            "multi_match" : {
                "query": title,
                "fields" : ["prefLabel^3", "related", "broader"]
            }
        }
    }
    with connect_elasticsearch() as es:
        res = find_n_best(es, IDX_NAME, query, n=10, label_colname='prefLabel')
    es.close()
    return res


def query_es_title_abstract(title, abstract):
    title = preprocess_text(title)
    abstract = preprocess_text(abstract)

    query = {
        "query": {

            "dis_max": {
                "queries": [
                    {
                        "multi_match" : {
                            "query": title,
                            "type": "best_fields",
                            "fields": ["prefLabel^4", "related", "broader"],
                            "tie_breaker": 0.5
                            }
                        },
                        {
                            "multi_match" : {
                            "query": abstract,
                            "analyzer" : "standard",
                            "type": "best_fields",
                            "fields": ["prefLabel^4", "related", "broader"],
                            "tie_breaker": 0.5
                            }
                        }
                    ]
                }
            }
        }
    with connect_elasticsearch() as es:
        res = find_n_best(es, IDX_NAME, query, n=10, label_colname='prefLabel')
    es.close()
    return res


def user_query(query):
    with connect_elasticsearch() as es:
        res = find_n_best(es, IDX_NAME, query, n=10, label_colname='prefLabel')
    es.close()
    return res