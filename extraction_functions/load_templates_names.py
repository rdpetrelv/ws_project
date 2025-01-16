import requests
from bs4 import BeautifulSoup
import os 

url = "https://bulbapedia.bulbagarden.net/wiki/Category:Infobox_templates"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:

    soup = BeautifulSoup(response.content, "html.parser")

    category_section = soup.find("div", class_="mw-category mw-category-columns")

    if category_section:

        template_links = category_section.find_all("a")
        
        template_names = [link.get_text() for link in template_links]
        
        print("Templates found:")
        #print("\n".join(template_names))
    else:
        print("Category section not found. The structure of the page might have changed.")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")


if len(template_names) > 0: 
    output_file = os.path.join("templates", "template_names.txt")
    template_name = [ template.split(":")[-1] for template in template_names ]
    with open(output_file, "w", encoding="utf-8") as file:
        for name in template_name:
            file.write(name + "\n")
    print(f"Template names saved to {output_file}")
else:
    print("No templates found to save.")