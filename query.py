from search import query_score
from commandlines import Command
import xml.etree.ElementTree as ET
from run import run







if __name__ == "__main__":
    c = Command()

    default_options = {
        'score': 'okapi-TF',
    }
    c.set_defaults(default_options)

    if c.contains_definitions('score'):
        score = c.get_definition('score')
    else :
        score = c.get_default('score')

    tree = ET.parse('topics.xml')
    document = tree.getroot()
    for quries in document:
        for query in quries:

            if query.tag == 'query':
                #print(f"from query {quries.attrib['number']}: query {query.text}")
                for document in query_score(score, query.text):
                    print(f"{quries.attrib['number']} 0 {document[2:]} run{run}")