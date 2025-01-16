from utils import *
import re 
from pyshacl import validate





def save_pokemon(page_title , template = "Pokémon") :

    page_title = f"{page_title} ({template})"
    print(page_title)

    out = fetch_page_data(page_title)
    # print(out) pour voire le resultats de query
    wikitext, links, images, templates = (
        out["parse"]["wikitext"]["*"],
        out["parse"]["links"],
        out["parse"]["images"],
        out["parse"]["templates"],
    )
    #print(templates)
    redirected_uri = resolve_redirect(wikitext)
    # print(redirected_uri)
    if redirected_uri is not None:
        out = fetch_page_data(redirected_uri)
        wikitext = out["parse"]["wikitext"]["*"]
        page_title = redirected_uri
    #print(wikitext)
    infobox_data = extract_infobox(wikitext)
    
    if infobox_data is None or not infobox_data:
        print("Not Good")
    else :
        if template == "Pokemon" or template == "Pokémon":
            shapes_file_path = "templates/shacl/pokemon.ttl"


            rdf_graph = generate_rdf_pokemon(
                infobox_data, images=None, links=links, page_title=page_title
            )
        elif template == "Ability" : 
            shapes_file_path = None
            rdf_graph = generate_rdf_ability(
                infobox_data, images=None, links=links, page_title=page_title
            )

        else :
            rdf_graph = generate_rdf(
                infobox_data, images=None, links=links, page_title=page_title
            )

        
        if template != "" and shapes_file_path is not None :
            shapes_graph = Graph()
            shapes_graph.parse(shapes_file_path, format="turtle")

            conforms, results_graph, results_text = validate(
                rdf_graph,
                shacl_graph=shapes_graph,
                ont_graph=None,
                inference='rdfs',
                abort_on_first=False,
                meta_shacl=False,
                debug=False
            )

            print("Conforms:", conforms)
            print("Results:")
            print(results_text)
        
        output_file1 = "database/pokemon.ttl"

        with open(output_file1, "w", encoding="utf-8") as f:
            f.write(rdf_graph.serialize(format="turtle"))
    time.sleep(1)


def list_all_pokemons() :
    page_title = "List of Pokémon by Kanto Pokédex number"
    out = fetch_page_data(page_title)
    wikitext, links, images, templates = (
        out["parse"]["wikitext"]["*"],
        out["parse"]["links"],
        out["parse"]["images"],
        out["parse"]["templates"],
    )

    pattern = r"\{\{rdex\|[0-9]+?\|[0-9]+?\|([^\|]+?)\|"

    pokemon_names = re.findall(pattern, wikitext)

    for pokemon in pokemon_names :
        save_pokemon(pokemon)



#list_all_pokemons()

save_pokemon("Slowbro" , template = "Pokémon")
