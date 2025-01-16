from utils import *
import re 


def get_pages_using_template(template_name = "Pokémon Infobox"):

    if template_name is None or template_name == " ":
        return []

    base_url = "https://bulbapedia.bulbagarden.net/w/api.php"
    continue_param = None  # Initialize continue parameter for pagination

    
    pages = []
    while True:
        params = {
            "action": "query",
            "list": "embeddedin",
            "eititle": f"Template:{template_name}",
            "eilimit": "max",
            "format": "json"
        }

        if continue_param:
            params.update(continue_param)
                  
        headers = {
            "User-Agent": "PokemonRDFBot/1.0 (https://example.com; your-email@example.com)"
        }

        response = requests.get(base_url, params=params , headers = headers)

        
       
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - Retrying after a short delay...")
            time.sleep(3)  # Retry after 5 seconds
            continue

        data = response.json()


        # Ensure the response has valid data
        if 'query' not in data or 'embeddedin' not in data['query']:
            print(f"Unexpected response format: {data}")
            break
        
        pages.extend(data['query']['embeddedin'])
        if 'continue' in data:
            # Add continue parameter if it exists
            #params["continue"] = data["continue"]
            continue_param = data["continue"]
            time.sleep(0.5)

        else:
            print(f"End of pages extraction for {template_name}")
            break
        print(f"Extracting files for template {template_name} and eicontinue {continue_param}")

    
    return [page['title'] for page in pages]

with open("templates/template_names.txt", "r", encoding="utf-8") as file:
    template_names_array = [line.strip() for line in file.readlines()]

def extract_data() : 
    parsed_uris = set()

    

    for template_name in template_names_array :
        print(f"Start extracting for {template_name}")
        pages = get_pages_using_template(template_name)
        count = 0
        print(len(pages))
        for page_title in pages: 
            if page_title in parsed_uris:
                    continue
            parsed_uris.add(page_title)

            if "Infobox" in page_title or "Bulbapedia" in page_title:
                continue 

            
            out = fetch_page_data(page_title , wait = 0.1)
            count += 1
            if out is not None and "parse" in out:
                links, externallinks = (
                        out["parse"]["wikitext"],
                        out["parse"]["links"],
                        out["parse"]["externallinks"],
                    )
            
            if wikitext is None: 
                continue

            if "*" not in wikitext :
                continue
            
            wikitext = wikitext["*"]

            if wikitext is None: 
                continue
            
            redirected_uri = resolve_redirect(wikitext)
            # print(redirected_uri)
            if redirected_uri is not None:
                parsed_uris.add(page_title)
                continue
            
            parsed_uris.add(page_title)

            page_title = re.sub(r'[^a-zA-Z0-9\s]', '', page_title).replace(" ", "_")

            

            if len(links) > 0 :
                output_file1 = f"data3/links/bulbapedia#{page_title}.txt"
                with open(output_file1, "w", encoding="utf-8") as f:
                    for link in links : 
                        f.write(link["*"])
                        f.write("\n")
            output_file1 = f"data3/wikitext/wikitext#{page_title}.txt"

            with open(output_file1, "w", encoding="utf-8") as f:
                f.write(wikitext)

            """
            if len(images) > 0 :
                output_file1 = f"data/images/bulbapedia#{page_title}.json"

                with open(output_file1, "w", encoding="utf-8") as f:
                    json.dump(images[0], f)
            """  
            if len(externallinks) > 0 :
                output_file1 = f"data3/externallinks/bulbapedia#{page_title}.txt"
                with open(output_file1, "w", encoding="utf-8") as f:
                    for externallink in externallinks :
                        f.write(externallink)
                        f.write("\n")
            print(f"Count : {count} template {template_name}")

extract_data()