# Bulbapedia Data Extraction Project

This project focuses on extracting Pokémon-related data from Bulbapedia. The goal is to extract entities associated with specific infoboxes dynamically, structure the data into a Knowledge Graph, and make the URIs resolvable through an interface. Below is an overview of the project's workflow and components.

## Overview

### Key Features

- **Entity Extraction**: Extracted all entities related to specific infobox templates.
- **Dynamic Wikitext Parsing**: Implemented a dynamic mechanism for extracting Wikitext of each entity.
- **Add Internal and External Links**: Added all the internal and external links within the entities.
- **Defining Entities**: Defined some entities and created our own vocabulary for this, available in the Vocabulary file.
- **Defining SHACLs**: Defined SHACL shapes for entities to validate the Knowledge Graph, available in the SHACL file.
- **Knowledge Graph**: Structured the extracted data into a graph with resolvable URIs.
- **Interface**: Developed an interface to interact with the data.

### Workflow

1. **Template Extraction**:

   - Extracted all existing infobox templates using `extraction_functions/load_templates_names.py`.
   - This script identifies and lists all infobox templates available on Bulbapedia.

2. **Page Fetching**:

   - Extracted all pages related to a specific infobox using `extraction_functions/fetch_by_infobox.py`.
   - This script fetches all pages corresponding to a given infobox template.

3. **Dynamic Wikitext Extraction**:

   - Dynamically extracted the Wikitext of each entity using `Bulbabot.ipynb`.
   - This notebook handles the parsing and structuring of Wikitext into usable data.
   - In the resourcesLis folder, there are stored the bulbapedia pages that uses a particular infobox template, that means for exmaple the file "character infobox.txt" conatains all the pages using the character infobox
   - Using pwiki as a the library to acces the bulbapedia meadiwiki api, here we read the resources list andfoer ach of them the extraction procedure is as follows:
   - First get the wiki text af that particular page, then look for the particular infobox template based on the regular expression that creates the infobox. LAso we parse the infobox in a dictionary of properties, proerty_values.
   - Using pwiki we algo get the images, internal link, i.e. pointing to ressources in bulbapedia, and external links, i.e., pointing to external pages.
   - Also for specific resources we defined the vocabulary definition, in the folder Vocabulary.
   - Then unsing the map_infobox_to_rdf funtion we generate an rdf graph and add their properties based on the vocabulary definition if it was defined. If the are not denifed int eh vocabulary we stated the objet as a literal. The outputs of the graps are in folders GeneratedGraph and GeneratedGraph1.
   - The BulbaMediaBot.ipynb is a fisrt draft version of this file.

4. **Interface Development**:

   - Created an interface for interacting with the Knowledge Graph.
   - Ensured all URIs are always resolvable by utilizing `server/` for hosting the interface.

5. **Utility Functions**:
   - `utils.py` contains various helper functions that facilitate different stages of the development process, such as data formatting, cleaning, and processing.

## Project Structure

```plaintext
.
├── extraction_functions/
│   ├── load_templates_names.py   # Extracts all infobox template names
│   ├── fetch_by_infobox.py       # Fetches pages related to specific infoboxes
├── Bulbabot.ipynb                # Dynamic extraction of Wikitext entities
├── server/                       # Hosts the interface for the Knowledge Graph
├── utils.py                      # Utility functions for various processes
├── Vocabulary file               # Contains defined vocabulary for entities
├── SHACL/*                       # Contains SHACL shapes for entity validation
└── README.md                     # Project documentation
```

## Knowledge Graph

The extracted data is structured into a Knowledge Graph that captures the relationships and attributes of Pokémon entities. The graph is accessible through:

- **Interface**: Hosted via the `server/` directory.
- **Resolvable URIs**: Ensures all entity URIs remain valid and accessible.

## Technologies Used

- **Python**: Core programming language for extraction and processing.
- **MediaWiki API**: Used for fetching Wikitext data from Bulbapedia.
- **Jupyter Notebook**: Facilitated dynamic extraction workflows.
- **Server Hosting**: Hosted the Knowledge Graph interface for user interaction.
- **Triple Store Fuseki** : used to host and serve the kwnoledge graph

## Usage

1. Run fuseki locally and create a database pokemon
2. Add to the fuseki pokemon datebase the ttl files of folder GeneratedGraph, GeneratedGraph1, Vocabulary
3. Run `server/app.py` to run the server.
