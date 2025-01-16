from flask import Flask, request, Response, redirect, render_template  , send_file
from rdflib import Graph
from urllib.parse import urlencode
from collections import defaultdict
import tempfile



import requests

app = Flask(__name__)

SPARQL_ENDPOINT = "http://localhost:3030/dataset/pokemon"  
namespace = ""


SPARQL_ENDPOINT = "http://localhost:3030/pokemon/sparql"

@app.route('/resource/<entity_type>/<entity_name>', methods=['GET'])
def resource(entity_type,entity_name):
    accept_header = request.headers.get("Accept", "")
    #print(f"Header is : " + accept_header)
    
    entity_uri = f"http://example.org/resource/{entity_type}/{entity_name}"

    if "text/turtle" in accept_header:
        query = f"""
        DESCRIBE <{entity_uri}>
        """
        response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "text/turtle"})
        print(f"response text : {response.text}")
        return Response(response.text, content_type="text/turtle")
    
    return redirect(f"/page/{entity_type}/{entity_name}")

@app.route('/page/<entity_type>/<entity_name>', methods=['GET'])
def page(entity_type,entity_name):
    entity_uri = f"http://example.org/resource/{entity_type}/{entity_name}"
    query = f"""
    DESCRIBE <{entity_uri}>
    """

    response = requests.get(SPARQL_ENDPOINT, params={"query": query, "format": "text/turtle"})
    if response.status_code == 200:
        g = Graph()
        g.parse(data=response.text, format="turtle")


        results = defaultdict(list)
        for s, p, o in g:
            if str(s) == entity_uri:  
                predicate = str(p)#g.qname(p) 
                value = str(o)
                results[predicate].append(value)
    return render_template("page.html" , entity_name = f"{entity_type}/{entity_name}" ,  results = results)


if __name__ == '__main__':
    app.run(debug=True)