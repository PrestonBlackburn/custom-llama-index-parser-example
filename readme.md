# Custom Parsing With Llama Index

We want to split a markdown file on h1 and h2 tags and provide relevant metadata about the document to LlamaIndex. It happens that h2 is a good level to split on, but Llama index does not provide the level of customization we want. To provide the level of control we need, we'll need to create a **custom node parser**. 

*Note that Llama index does provide a couple Markdown parsers may fit your use case.*

#### splitters vs parsers
Effectively we can think of these as mostly the same thing. Both implment a `get_nodes_from_documents()` that will return a list of nodes. They eventually inherit from the `NodeParser` classes, but the splitters seem to have intermediate text splitter classes to handle more complex logic. As far as I can tell that is the main difference.    

- **Node Parsers** - These class inherit from the `NodeParser` class. Node parsers are the default for most files.
- **Splitters** - These classes inherit from `MetadataAwareTextSplitter` which inherits from `TextSplitter` class and finally `NodeParser`. The additional logic appears to try and split text in a more logical manner than the standard node parsers. 

### Basic Llama index flow
1. Read data to create "documents". Llama index referes to the source data before processing as documents, but we can imediately read the documents as nodes.  
2. Process nodes with a NodeParser or Splitter. This is where the main processing logic will be handled to create a new list of processed nodes.  
3. Now we can create a vector store index from the parsed nodes we created.  
4. The vector store index can then be used for RAG queries.  

To see an example of the custom node parser being used end to end, check out the `tests/test_end_to_end.py` file.


### Testing
Example running with pytest
```python
python -m pytest
```
