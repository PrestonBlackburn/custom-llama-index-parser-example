"""Custom Markdown node parser."""

from typing import Any, Dict, List, Optional, Sequence
import logging

from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.node_parser.node_utils import build_nodes_from_splits
from llama_index.core.schema import BaseNode, MetadataMode, TextNode
from llama_index.core.utils import get_tqdm_iterable


_logger = logging.getLogger(__name__)

# Uses TextNode and BaseNode


class HeadingMarkdownNodeParser(NodeParser):
    """Custom Markdown node parser.

    Splits a document into Nodes using custom Markdown splitting logic to split based on heading levels.

    Args:
        include_metadata (bool): whether to include metadata in nodes
        heading_level (int): level of heading to split on

    """

    @classmethod
    def from_defaults(
        cls,
        include_metadata: bool = True,
        include_prev_next_rel: bool = True,
        callback_manager: Optional[CallbackManager] = None,
    ) -> "HeadingMarkdownNodeParser":
        callback_manager = callback_manager or CallbackManager([])

        return cls(
            include_metadata=include_metadata,
            include_prev_next_rel=include_prev_next_rel,
            callback_manager=callback_manager,
        )

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "HeadingMarkdownNodeParser"

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[BaseNode]:
        all_nodes: List[BaseNode] = []
        nodes_with_progress = get_tqdm_iterable(nodes, show_progress, "Parsing nodes")

        for node in nodes_with_progress:
            nodes = self.get_nodes_from_node(node, **kwargs)
            all_nodes.extend(nodes)

        return all_nodes

    def _headings_processor(
        self, segments: list, headings: list, current_heading: str, level: int
    ) -> List[str]:
        # add back the headings if they were split on

        splits = []
        # heading level corresponds to #, ##, ###, etc.
        heading_level = level + 1

        for segment in segments:
            segment_has_parent = [
                segment.startswith(parent_heading)
                for parent_heading in headings[0:heading_level]
            ]

            if True in segment_has_parent:
                for parent_heading in headings[0:heading_level]:
                    if segment.startswith(parent_heading):
                        splits.append(segment)

            else:
                splits.append(current_heading + segment)

        return splits

    def _document_splitter(
        self,
        heading: str,
        document: list,
        heading_level: int,
        headings: list = ["\n# ", "\n## ", "\n### ", "\n#### "],
    ) -> List[str]:
        documents = []
        split_docs = []

        for doc in document:

            if heading not in doc:
                # If the heading is not at the current level, then don't process the doc
                _logger.debug(f"skipping doc {doc[0:100]}")
                split_docs.append(doc)

            else:
                _logger.debug(f"processing doc:  {doc[0:100]}")
                segments = doc.split(heading)

                # if the heading doesn't start with a previous heading then add current heading
                splits = self._headings_processor(
                    segments, headings, heading, heading_level
                )

                split_docs.extend(splits)

            documents.extend(split_docs)
            split_docs = []

        return documents

    def _split_on_heading(self, document: str, heading_level: int = 2) -> List[str]:
        split_headings = []
        document = [document]

        for i in range(heading_level):
            split_on = "\n" + "#" * (i + 1) + " "
            split_headings.append(split_on)

        for current_level, heading in enumerate(split_headings):
            _logger.debug(f"splitting on: {heading}")

            document = self._document_splitter(heading, document, current_level)

        return document

    def _get_heading_text(
        self, heading_sections: list, heading_level: int = 2
    ) -> List[tuple]:
        """Get heading text as metadata. Track parent heading names"""

        # get the different heading prefixes we need
        heading_level_text = [
            "#" * heading + " " for heading in range(1, heading_level + 1)
        ]
        heading_level_start = ["\n" + str(heading) for heading in heading_level_text]
        heading_level_h_tag = [
            "Header " + str(heading) for heading in range(1, heading_level + 1)
        ]

        # initialize metadata
        metadata = {heading_level_h_tag[i]: None for i in range(heading_level)}

        heading_w_metadata = []
        last_max = 0
        current_max = 0

        for heading in heading_sections:
            # reset metadata (ex: h2 up to -> h1)
            if last_max > current_max:
                metadata = {heading_level_h_tag[i]: None for i in range(heading_level)}

            for i in range(heading_level):
                if heading.startswith(heading_level_start[i]):
                    current_max = i
                    heading = heading.replace(heading_level_start[i], "")
                    metadata[heading_level_h_tag[i]] = heading.split("\n")[0].strip()
                    break
                else:
                    continue

            heading_w_metadata.append((heading, metadata.copy()))

            last_max = current_max

        return heading_w_metadata

    def get_nodes_from_node(self, node: BaseNode, **kwargs) -> List[TextNode]:
        """Get Nodes from document basedon headers"""
        text = node.get_content(metadata_mode=MetadataMode.NONE)
        markdown_nodes = []

        # heading level can get passed as kwargs
        headings = self._split_on_heading(text, **kwargs)
        headings_w_metadata = self._get_heading_text(headings, **kwargs)

        for heading, metadata in headings_w_metadata:
            markdown_nodes.append(self._build_node_from_split(heading, node, metadata))

        return markdown_nodes

    def _build_node_from_split(
        self,
        text_split: str,
        node: BaseNode,
        metadata: dict,
    ) -> TextNode:
        """Build node from single text split."""

        node = build_nodes_from_splits([text_split], node, id_func=self.id_func)[0]

        if self.include_metadata:
            node.metadata = {**node.metadata, **metadata}

        return node


if __name__ == "__main__":

    from llama_index.readers.file import FlatReader
    from pathlib import Path

    md_docs = FlatReader().load_data(Path("example_source.md"))

    print(md_docs)
    print(len(md_docs))

    parser = HeadingMarkdownNodeParser()
    nodes = parser.get_nodes_from_documents(md_docs, heading_level=2)

    print(nodes)
    print(len(nodes))

    assert len(nodes) == 5
