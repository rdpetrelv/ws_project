from utils import *
import re 
import json





# Fetch all pages avec query
def extract_infobox(api_url):
    
    continue_param = "Alolan_Persian_(All_Stars_Collection_GX_Starter_Deck_92)"
    parsed_uris = set()



    while True:
        print("Extracting pages : =======================================")

        pages = []
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
            time.sleep(3)  # Retry after 5 seconds
            continue

        data = response.json()

        # Extract pages
        pages.extend([page["title"] for page in data["query"]["allpages"]])

        # Check for continuation
        if "continue" in data:
            continue_param = data["continue"]["apcontinue"]
        else:
            print("End of pages extraction")
            break

        print(f"Extracted pages apcontinue : {continue_param}  =======================================")
        count = 0 
        wait = 0
        for page_title in pages:
            page_title = page_title

            if page_title in parsed_uris:
                continue
            if count == 20 :
                print("Change wait time")
                wait = 0.5
                count = 0 
            print(f"count {count}")
            out = fetch_page_data(page_title , wait)
            count += 1 
            wait = 0 
            # print(out) pour voire le resultats de query
            if out["parse"] is not None : 
                wikitext, links, externallinks = (
                        out["parse"]["wikitext"],
                        out["parse"]["links"],
                        out["parse"]["externallinks"],
                    )
            else : 
                continue
            if wikitext is None: 
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

            output_file1 = f"data/wikitext/wikitext#{page_title}.txt"

            with open(output_file1, "w", encoding="utf-8") as f:
                f.write(wikitext)
            
            if len(links) > 0 :
                output_file1 = f"data3/links/bulbapedia#{page_title}.txt"
                with open(output_file1, "w", encoding="utf-8") as f:
                    for link in links : 
                        f.write(link["*"])
                        f.write("\n")

            if len(externallinks) > 0 :
                output_file1 = f"data3/externallinks/bulbapedia#{page_title}.txt"
                with open(output_file1, "w", encoding="utf-8") as f:
                    for externallink in externallinks :
                        f.write(externallink)
                        f.write("\n")



        # Add delay to avoid rate-limiting
        time.sleep(0.5)

        
extract_infobox(API_URL)