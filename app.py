from utils import *


count = 0

parsed_uris = set()
# Here try to have all the pages of bulbapedia
pages = fetch_all_pages(API_URL)

for page_title in pages:
    if page_title in parsed_uris:
        continue

    out = fetch_page_data(page_title)
    # print(out) pour voire le resultats de query
    wikitext, links, images, templates = (
        out["parse"]["wikitext"]["*"],
        out["parse"]["links"],
        out["parse"]["images"],
        out["parse"]["templates"],
    )
    redirected_uri = resolve_redirect(wikitext)
    # print(redirected_uri)
    if redirected_uri is not None:
        if redirected_uri in parsed_uris:
            continue
        out = fetch_page_data(redirected_uri)
        wikitext = out["parse"]["wikitext"]["*"]
        parsed_uris.add(page_title)
        page_title = redirected_uri
    infobox_data = extract_infobox(wikitext)
    if infobox_data is None or not infobox_data:
        continue

    parsed_uris.add(page_title)
    rdf_graph = generate_rdf(
        infobox_data, image=None, links=links, page_title=page_title
    )

    output_file1 = f"graphOut/bulbapedia_graph{page_title}.ttl"

    with open(output_file1, "w", encoding="utf-8") as f:
        f.write(rdf_graph.serialize(format="turtle"))

    print(rdf_graph.serialize(format="turtle"))

    count += 1
    if count > 10:  # pour visulaiser les 10 premiers pages
        break


# this function is used to extract the pokedex-i18n.tsv
def extract_pokedex_file():

    file_path = "pokedex-i18n.tsv"
    rdf_graph = process_pokedex_file(file_path)

    output_file = "pokedex_labels.ttl"

    # Save RDF graph to a Turtle file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rdf_graph.serialize(format="turtle"))

    print(f"RDF graph saved to {output_file}")



    

def save_pokemon(page_title) :

    page_title = f"{page_title} (Pokémon)"

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
    infobox_data = extract_infobox(wikitext)
    
    if infobox_data is None or not infobox_data:
        print("Not Good")
    else :

        rdf_graph = generate_rdf_pokemon(
            infobox_data, image=None, links=links, page_title=page_title
        )
        output_file1 = "database/data.ttl"

        with open(output_file1, "w", encoding="utf-8") as f:
            f.write(rdf_graph.serialize(format="turtle"))




# execute list_all_pokemons for retreiving pokemons data 
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


list_all_pokemons()