from llama_index.core import VectorStoreIndex
from llama_index.readers.file import FlatReader
from llama_index.core.node_parser import MarkdownNodeParser
from pathlib import Path
import pytest

from custom_md_node_parser import HeadingMarkdownNodeParser


@pytest.fixture
def documents():
    documents = FlatReader().load_data(Path("tests/example_source.md"))

    assert len(documents) == 1

    return documents


def test_custom_parser(documents):

    parser = HeadingMarkdownNodeParser()
    nodes = parser.get_nodes_from_documents(documents, heading_level=2)

    # here we only have nodes for h1 and h2 level headings
    assert len(nodes) == 5

    index = VectorStoreIndex(nodes)
    query_engine = index.as_query_engine()
    response = query_engine.query("Where is h1a-h2b-h3a")

    node_metadata = [node.metadata for node in response.source_nodes]

    expected_metadata = {
        "Header 1": "Example H1 - Section B",
        "Header 2": "Example h2 in section b",
        "filename": "example_source.md",
        "extension": ".md",
    }

    assert expected_metadata in node_metadata


def test_vanilla_parser(documents):

    parser = MarkdownNodeParser()
    nodes = parser.get_nodes_from_documents(documents)

    # notice the vanilla parser produces a node for each heading
    assert len(nodes) == 7

    index = VectorStoreIndex(nodes)
    query_engine = index.as_query_engine()
    response = query_engine.query("Where is h1a-h2b-h3a")

    node_metadata = [node.metadata for node in response.source_nodes]

    # in this case "Header 2" doesn't contain any information from is Header 3 subheading
    expected_metadata = {
        "Header 1": "Example H1 - Section B",
        "Header 2": "Example h2 in section b",
        "filename": "example_source.md",
        "extension": ".md",
    }

    assert expected_metadata in node_metadata
