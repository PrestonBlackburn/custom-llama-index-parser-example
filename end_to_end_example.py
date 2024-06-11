from llama_index.core import VectorStoreIndex
from llama_index.readers.file import FlatReader
from pathlib import Path
import pytest

from custom_md_node_parser import HeadingMarkdownNodeParser

documents = FlatReader().load_data(Path("example_source.md"))

parser = HeadingMarkdownNodeParser()
nodes = parser.get_nodes_from_documents(documents, heading_level = 2)

index = VectorStoreIndex(nodes)
query_engine = index.as_query_engine()
response = query_engine.query("Where is h1a-h2b-h3a")
print(response)