from utils import *
import re 




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
            infobox_data, images=None, links=links, page_title=page_title
        )
        output_file1 = "database/data.ttl"

        with open(output_file1, "w", encoding="utf-8") as f:
            f.write(rdf_graph.serialize(format="turtle"))



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

#save_pokemon("Slowbro")
