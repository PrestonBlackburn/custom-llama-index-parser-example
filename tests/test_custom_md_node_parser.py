from llama_index.readers.file import FlatReader
from pathlib import Path
import pytest

from custom_md_node_parser import HeadingMarkdownNodeParser


@pytest.fixture
def test_doc():
    md_docs = FlatReader().load_data(Path("tests/example_source.md"))
    assert len(md_docs) == 1

    return md_docs


@pytest.fixture
def parsed_doc(test_doc):
    parser = HeadingMarkdownNodeParser()
    nodes = parser.get_nodes_from_documents(test_doc, heading_level=2)
    return nodes


def test_length(parsed_doc):
    assert len(parsed_doc) == 5


def test_metadata_h1(parsed_doc):
    first_h1_metadata = {
        "Header 1": "# Example H1 - Section A",
        "Header 2": None,
        "filename": "example_source.md",
        "extension": ".md",
    }
    assert first_h1_metadata == parsed_doc[0].metadata


def test_metadata_h2(parsed_doc):
    last_h2_metadata = metadata = {
        "Header 1": "Example H1 - Section B",
        "Header 2": "Example h2 in section b",
        "filename": "example_source.md",
        "extension": ".md",
    }
    assert last_h2_metadata == parsed_doc[-1].metadata
