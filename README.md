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

## Usage
1. Run `server/app.py` to run the server.


