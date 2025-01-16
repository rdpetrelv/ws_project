from utils import *


graph = process_pokedex_file("./pokedex-i18n.tsv")

graph.serialize(destination="pokedex_labels.ttl", format="turtle")