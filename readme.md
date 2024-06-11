# Custom Parsing With Llama Index

We want to split a markdown file on h1 and h2 tags and provide relevant metadata about the document to LlamaIndex. It happens that h2 is a good level to split on, but Llama index does not provide the level of customization we want. To provide the level of control we need, we'll need to create a **custom node parser**. 

*Note that Llama index does provide a couple Markdown parsers may fit your use case.*

splitters vs parsers -
Some splitters inherit from the NodeParser base class, and the other parsers inherit from the NodeParser as well. Seem to be a little more ad-hoc with naming (parser vs splitter)


Custom Docs -> Custom Transforms (to nodes) -> Load Nodes to Index  
 
Custom Splitting: Then the text splitter gets passed into the node parser, which also gets passed into service context  
Custom Transforms: A transformation is something that takes a list of nodes as an input, and returns a list of nodes.

NodeParser: Node parsers are a simple abstraction that take a list of documents, and chunk them into Node objects  

Splitters can be wrapped by node parser




### Llama index flow:
1. Read Docs / create Documents
2. Split objects + create nodes (transforms)
3. Load vector index




# Testing

```python
python -m pytest
```
