import time
from bs4 import BeautifulSoup
import requests
import wikitextparser as wtp
from rdflib import Graph, URIRef, Literal, Namespace , BNode
from rdflib.namespace import RDF, RDFS, FOAF, XSD
import csv

from collections import defaultdict

import validators


LOCAL_URI = Namespace("http://localhost:8000/resource/")
BASE = Namespace("https://bulbapedia.bulbagarden.net/w/")
SCHEMA = Namespace("https://schema.org/")
DBPEDIA = Namespace("http://dbpedia.org/resource/")
YAGO = Namespace("http://yago-knowledge.org/resource/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")

API_URL = "https://bulbapedia.bulbagarden.net/w/api.php"


# extraire tous les noms d'infoboxes
with open("templates/template_names.txt", "r", encoding="utf-8") as file:
    template_names_array = [line.strip() for line in file.readlines()]

# on doit faire un mapping qui fait le map entre proprieté dans infobox et ce qu'on va utiliser
rdf_mapping = {
    "name": "schema:name",  # Name of the Pokémon
    "jname": "ex:japaneseName",  # Japanese name
    "tmname": "ex:transliteratedName",  # Transliterated name
    "ndex": "schema:identifier",  # National Pokédex number
    "type1": "ex:type1",  # Primary type
    "type2": "ex:type2",  # Secondary type
    "category": "schema:category",  # Category (e.g., Seed Pokémon)
    "height-ftin": "ex:heightFtIn",  # Height in feet and inches
    "height-m": "schema:height",  # Height in meters
    "weight-lbs": "ex:weightLbs",  # Weight in pounds
    "weight-kg": "schema:weight",  # Weight in kilograms
    "abilityn": "ex:abilityCount",  # Number of abilities
    "ability1": "ex:primaryAbility",  # Primary ability
    "abilityd": "ex:hiddenAbility",  # Hidden ability
    "egggroupn": "ex:eggGroupCount",  # Number of egg groups
    "egggroup1": "ex:eggGroup1",  # First egg group
    "egggroup2": "ex:eggGroup2",  # Second egg group
    "eggcycles": "ex:eggCycles",  # Number of egg cycles
    "evtotal": "ex:evTotal",  # Total EV points
    "evsa": "ex:specialAttackEV",  # Special Attack EV
    "expyield": "ex:baseExperienceYield",  # Base experience yield
    "oldexp": "ex:oldExperienceYield",  # Old experience yield
    "lv100exp": "ex:level100Experience",  # Experience to reach level 100
    "gendercode": "ex:genderCode",  # Gender ratio code
    "color": "schema:color",  # Color classification
    "catchrate": "ex:catchRate",  # Catch rate
    "body": "ex:bodyShape",  # Body shape code
    "generation": "ex:generation",  # Pokémon generation
    "pokefordex": "ex:pokedexEntry",  # Pokédex entry URL or identifier
    "friendship": "ex:baseFriendship",  # Base friendship level
}


# Fetch une page en se basant sur le nom de la page
def fetch_page_data(page_title):
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "wikitext|templates|images|links",
        "format": "json",
    }

    headers = {
        "User-Agent": "PokemonRDFBot/1.0 (https://example.com; your-email@example.com)"
    }

    response = requests.get(API_URL, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


# Fetch all pages avec query
def fetch_all_pages(api_url):
    pages = []
    continue_param = None

    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "aplimit": "max",
            "format": "json",
        }
        if continue_param:
            params["apcontinue"] = continue_param

        headers = {
            "User-Agent": "PokemonRDFBot/1.0 (https://example.com; your-email@example.com)"
        }

        response = requests.get(api_url, params=params, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code} - Retrying after a short delay...")
            time.sleep(5)  # Retry after 5 seconds
            continue

        data = response.json()

        # Extract pages
        pages.extend([page["title"] for page in data["query"]["allpages"]])

        # Check for continuation
        if "continue" in data:
            continue_param = data["continue"]["apcontinue"]
        else:
            break

        # Add delay to avoid rate-limiting
        time.sleep(1)  # Delay of 1 second between requests

        break  # a modifier plus tard si tu veux extraire tous les pages

    return pages


# fetch using web scrapping don(t use this
def fetch_infobox(page_title):
    page_url = (
        f"https://bulbapedia.bulbagarden.net/w/index.php?title={page_title}&action=edit"
    )
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")

    infobox = soup.find(id="wpTextbox1")  # Example infobox class
    if infobox:
        text_content = infobox.get_text(strip=True)
        image_url = f"https://bulbapedia.bulbagarden.net/wiki/{page_title}"
        response = requests.get(image_url)
        soup2 = BeautifulSoup(response.text, "html.parser")
        table = soup2.find("table", class_="roundy")
        if table:
            first_img = table.find("img")
            if first_img:

                return text_content, first_img["src"]
            else:
                return text_content, None
    return None


# for extracting wikitext
def extract_infobox(wikitext):
    parsed = wtp.parse(wikitext)
    templates = parsed.templates
    for template in templates:
        for tmp in template_names_array:
            if tmp in template.name:
                return {
                    param.name.strip(): param.value.strip()
                    for param in template.arguments
                }
    return None


def resolve_redirect(content):
    parsed = wtp.parse(content)
    if parsed.string and parsed.string.strip().startswith("#REDIRECT"):
        redirect_match = parsed.string.strip().split("[[", 1)[-1].split("]]", 1)[0]
        redirect_target = redirect_match.strip()
        return redirect_target
    return None


# to validate a URI
def is_valid_uri(uri):
    return validators.url(uri)


# Generate rdf to change this function so we use as much as we can schema.org
def generate_rdf_pokemon(infobox_data, images=False, links=None, page_title=None):
    g = Graph()
    g.bind("local", LOCAL_URI)
    g.bind("base", BASE)
    g.bind("schema", SCHEMA)
    g.bind("owl", OWL)


    seen = set()

    page_uri = URIRef(f"{BASE}page/{page_title.replace(' ', '_')}")
    entity_uri = URIRef(f"{LOCAL_URI}{page_title.replace(' ', '_')}")

    g.add((page_uri, RDF.type, FOAF.Document))
    g.add((page_uri, FOAF.primaryTopic, entity_uri))

    
    blank_node = BNode() 
    if "form1" in infobox_data : 
        g.add((blank_node , SCHEMA.name , Literal(infobox_data["form1"])))
    value = infobox_data["type1"]
    title_type = f"{value} (Type)"
    g.add((blank_node, RDF.type, URIRef(f"{LOCAL_URI}{title_type.replace(' ', '_')}")))
    if "type2" in infobox_data :
        value = infobox_data["type2"]
        title_type = f"{value} (Type)"
        g.add((blank_node, RDF.type, URIRef(f"{LOCAL_URI}{title_type.replace(' ', '_')}")))
    mapping = {
        "ability1" : "ability",
        "ability2" : "ability" ,
        "abilitym" : "mega_ability",
        "abilitym2" : "mega_ability",
        "abilityd" : "hidden_ability",
        "abilityd2" : "hidden_ability",
    }
    for ability in ["ability1" , "ability2" , "abilitym" , "abilitym2" , "abilityd2" ,"abilityd"] :
        if ability in infobox_data :
            value = infobox_data[ability]
            page_type = f"{value} (Ability)"
            predicate = LOCAL_URI[mapping[ability].replace(" ", "_")]
            g.add((blank_node, predicate, URIRef(f"{LOCAL_URI}{page_type.replace(' ', '_')}")))
    for ev in ["evhp" , "evat" , "evde" , "evsa" , "evsd" , "evsp"] :
        if ev in infobox_data:
            value = infobox_data[ev]
            predicate = LOCAL_URI[ev]
            g.add((blank_node, predicate, Literal(value)))

    height_blank_node = BNode()
    g.add((height_blank_node, SCHEMA.description, Literal("The height of the pokemon character in fits ")))
    g.add((height_blank_node, SCHEMA.value, Literal(infobox_data["height-ftin"])))
    g.add((height_blank_node, SCHEMA.unitText , Literal("fits")))
    g.add((blank_node , SCHEMA.height, height_blank_node))

    height_blank_node = BNode()
    g.add((height_blank_node, SCHEMA.description, Literal("The height of the pokemon character in meters ")))
    g.add((height_blank_node, SCHEMA.value, Literal(infobox_data["height-m"])))
    g.add((height_blank_node, SCHEMA.unitText , Literal("meters")))
    g.add((blank_node , SCHEMA.height, height_blank_node))


    weight_blank_node = BNode()
    g.add((weight_blank_node, SCHEMA.description, Literal("The weight of the pokemon character in lbs")))
    g.add((weight_blank_node, SCHEMA.value, Literal(infobox_data["weight-lbs"])))
    g.add((weight_blank_node, SCHEMA.unitText , Literal("weight-lbs")))
    g.add((blank_node , SCHEMA.weight, weight_blank_node))

    weight_blank_node = BNode()
    g.add((weight_blank_node, SCHEMA.description, Literal("The weight of the pokemon character in kg")))
    g.add((weight_blank_node, SCHEMA.value, Literal(infobox_data["weight-kg"])))
    g.add((weight_blank_node, SCHEMA.unitText , Literal("weight-kg")))
    g.add((blank_node , SCHEMA.weight, weight_blank_node))


    
    
    if "image" in infobox_data : 
        g.add((blank_node , SCHEMA.image , Literal(infobox_data['image'])))

    predicate = LOCAL_URI["principal_form"]

    g.add((entity_uri , predicate , blank_node ))
    seen.update({"name" , "egggroup1" , "egggroup2" , "evhp" , "evat" , "evde" , "evsa" , "evsd" , "evsp" ,"weight-kg" , "weight-lbs" , "height-ftin" , "height-m" , "tmname" , "jname" ,"type1" , "type2" , "ability1" , "ability2" , "abilitym" , "abilitym2" , "abilityd2" ,"abilityd" , "form1" , "image"})

    for i in range(2 , 7) :
        form_name = f"form{i}"
        if form_name not in infobox_data : 
            break

        blank_node = BNode() 
        
        g.add((blank_node , SCHEMA.name , Literal(infobox_data[form_name])))
        if f"{form_name}type1" in infobox_data :
            value = infobox_data[f"{form_name}type1"]
            title_type = f"{value} (Type)"
            g.add((blank_node, RDF.type, URIRef(f"{LOCAL_URI}{title_type.replace(' ', '_')}")))
        if f"{form_name}type2" in infobox_data :
            value = infobox_data[f"{form_name}type2"]
            title_type = f"{value} (Type)"
            g.add((blank_node, RDF.type, URIRef(f"{LOCAL_URI}{title_type.replace(' ', '_')}")))
        mapping = {
            f"ability{i}-1" : "ability",
            f"ability{i}-2" : "ability",
        }
        for ability in [f"ability{i}-1" , f"ability{i}-2"] :
            if ability in infobox_data :
                value = infobox_data[ability]
                page_type = f"{value} (Ability)"
                predicate = LOCAL_URI[mapping[ability].replace(" ", "_")]
                g.add((blank_node, predicate, URIRef(f"{LOCAL_URI}{page_type.replace(' ', '_')}")))
        
        for ev in [f"evhp{i}" , f"evat{i}" , f"evde{i}" , f"evsa{i}" , f"evsd{i}" , f"evsp{i}"] :
            if ev in infobox_data:
                value = infobox_data[ev]
                predicate = LOCAL_URI[ev]
                g.add((blank_node, predicate, Literal(value)))

        if f"height-ftin{i}" in infobox_data :
            height_blank_node = BNode()
            g.add((height_blank_node, SCHEMA.description, Literal("The height of the pokemon character in fits ")))
            g.add((height_blank_node, SCHEMA.value, Literal(infobox_data["height-ftin"])))
            g.add((height_blank_node, SCHEMA.unitText , Literal("ftin")))
            g.add((blank_node , SCHEMA.height, height_blank_node))

        if f"height-m{i}" in infobox_data :
            height_blank_node = BNode()
            g.add((height_blank_node, SCHEMA.description, Literal("The height of the pokemon character in meters ")))
            g.add((height_blank_node, SCHEMA.value, Literal(infobox_data["height-m"])))
            g.add((height_blank_node, SCHEMA.unitText , Literal("meters")))
            g.add((blank_node , SCHEMA.height, height_blank_node))

        if f"weight-lbs{i}" in infobox_data :
            weight_blank_node = BNode()
            g.add((weight_blank_node, SCHEMA.description, Literal("The weight of the pokemon character in lbs")))
            g.add((weight_blank_node, SCHEMA.value, Literal(infobox_data["weight-lbs"])))
            g.add((weight_blank_node, SCHEMA.unitText , Literal("weight-lbs")))
            g.add((blank_node , SCHEMA.weight, weight_blank_node))
        
        if f"weight-kg{i}" in infobox_data :
            weight_blank_node = BNode()
            g.add((weight_blank_node, SCHEMA.description, Literal("The weight of the pokemon character in kg")))
            g.add((weight_blank_node, SCHEMA.value, Literal(infobox_data["weight-kg"])))
            g.add((weight_blank_node, SCHEMA.unitText , Literal("weight-kg")))
            g.add((blank_node , SCHEMA.weight, weight_blank_node))
        
        
        if f"image{i}" in infobox_data : 
            g.add((blank_node , SCHEMA.image , Literal(infobox_data[f'image{i}'])))

        predicate = LOCAL_URI["form"]

        g.add((entity_uri , predicate , blank_node ))
        seen.update({f"evhp{i}" , f"evat{i}" , f"evde{i}" , f"evsa{i}" , f"evsd{i}" , f"evsp{i}" , f"height-ftin{i}" , f"weight-kg{i}", f"height-m{i}", f"weight-lbs{i}", f"{form_name}type1" , f"{form_name}type2" , f"ability{i}-1" , f"ability{i}-2" , form_name , f"image{i}"})


    if 'egggroup1' in infobox_data :
    
        value = infobox_data["egggroup1"]
        title_egg = f"{value} (Egg Group)"
        predicate = LOCAL_URI["egg_group"]

        g.add((entity_uri, predicate, URIRef(f"{LOCAL_URI}{title_egg.replace(' ', '_')}")))
    if 'egggroup2' in infobox_data :
    
        value = infobox_data["egggroup2"]
        title_egg = f"{value} (Egg Group)"
        predicate = LOCAL_URI["egg_group"]

        g.add((entity_uri, predicate, URIRef(f"{LOCAL_URI}{title_egg.replace(' ', '_')}")))

    for key, value in infobox_data.items():
        if key not in seen : 
            predicate = LOCAL_URI[key.replace(" ", "_")]
            g.add((entity_uri, predicate, Literal(value)))

    if "name" in infobox_data:
        g.add((entity_uri, SCHEMA.name, Literal(infobox_data["name"])))

    
    

    if links is not None:
        for link in links:
            if "exists" in link:
                link_name = link["*"]
                link_uri = URIRef(
                    f"http://bulbapedia.org/wiki/{link_name.replace(' ', '_')}"
                )
                if is_valid_uri(link_uri):
                    g.add((entity_uri, RDFS.seeAlso, link_uri))
    

    dbpedia_uri = URIRef(f"{DBPEDIA}{page_title.replace(' ', '_')}")
    yago_uri = URIRef(f"{YAGO}{page_title.replace(' ', '_')}")

    g.add((entity_uri, OWL.sameAs, dbpedia_uri))
    g.add((entity_uri, OWL.sameAs, yago_uri))

    return g


# Generate rdf to change this function so we use as much as we can schema.org
def generate_rdf(infobox_data, image=False, links=None, page_title=None):
    g = Graph()
    g.bind("local", LOCAL_URI)
    g.bind("base", BASE)
    g.bind("schema", SCHEMA)
    g.bind("owl", OWL)

    page_uri = URIRef(f"{BASE}page/{page_title.replace(' ', '_')}")
    entity_uri = URIRef(f"{LOCAL_URI}{page_title.replace(' ', '_')}")

    g.add((page_uri, RDF.type, FOAF.Document))
    g.add((page_uri, FOAF.primaryTopic, entity_uri))
    g.add((entity_uri, RDF.type, FOAF.primaryTopic))
    # g.add((entity_uri, FOAF.name, Literal(page_title)))

    for key, value in infobox_data.items():
        predicate = LOCAL_URI[key.replace(" ", "_")]
        g.add((entity_uri, predicate, Literal(value)))

    if image:
        g.add((entity_uri, SCHEMA.image, Literal(image)))

    if links is not None:
        for link in links:
            if "exists" in link:
                link_name = link["*"]
                link_uri = URIRef(
                    f"http://bulbapedia.org/wiki/{link_name.replace(' ', '_')}"
                )
                if is_valid_uri(link_uri):
                    g.add((entity_uri, RDFS.seeAlso, link_uri))

    dbpedia_uri = URIRef(f"{DBPEDIA}{page_title.replace(' ', '_')}")
    yago_uri = URIRef(f"{YAGO}{page_title.replace(' ', '_')}")

    g.add((entity_uri, OWL.sameAs, dbpedia_uri))
    g.add((entity_uri, OWL.sameAs, yago_uri))

    return g


# This function process pokedex-i18.tsv
def process_pokedex_file(file_path):

    my_dict = defaultdict(list)

    g = Graph()
    g.bind("local", LOCAL_URI)
    g.bind("schema", SCHEMA)

    language_mapping = {
        "Italian": "it",
        "French": "fr",
        "Chinese": "zh-Hant",  # Traditional Chinese
        "English": "en",
        "Japanese": "ja",
        "Czech": "cs",
        "Korean": "ko",
        "German": "de",
        "Spanish": "es",
        "Official roomaji": "ja-Latn",  # Romanized Japanese (ISO-compliant)
    }

    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            entity_type = row["type"]
            entity_id = row["id"]
            label = row["label"]
            language = row["language"]

            my_dict[f"{entity_type}.{entity_id}"].append(
                f"{label}@{language_mapping.get(language, None)}"
            )

    for key in my_dict:
        entity_type, entity_id = key.split(".")
        values = my_dict[key]
        entity_uri = None
        for label_l in values:
            label, lang_tag = label_l.split("@")[0], label_l.split("@")[1]
            if lang_tag == "en":
                entity_uri = URIRef(
                    f"{LOCAL_URI}{entity_type}/{label.replace(' ', '_')}"
                )
                break

        if entity_uri is not None:
            for label_l in values:
                label, lang_tag = label_l.split("@")[0], label_l.split("@")[1]
                g.add((entity_uri, SCHEMA.name, Literal(label, lang=lang_tag)))
        else:
            print(f"{lang_tag}")
            print(values)

    return g
