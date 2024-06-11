""" Vanilla markdown parser (no llama index)"""
import logging

_logger = logging.getLogger(__name__)

def headings_processor(segments:list, headings:list, current_heading:str, level:int ):
    # add back the headings if they were split on

    splits = []
    # heading level corresponds to #, ##, ###, etc.
    heading_level = level + 1

    for segment in segments:
        segment_has_parent = [segment.startswith(parent_heading) for parent_heading in headings[0:heading_level]]
    
        if True in segment_has_parent:
            for parent_heading in headings[0:heading_level]:
                if segment.startswith(parent_heading):
                    splits.append(segment)

        else:
            splits.append(current_heading + segment)

    return splits


   
def document_splitter(heading: str, 
                      document: list, 
                      level: int,
                      headings:list = ["\n# ", "\n## ", "\n### ", "\n#### "]
                     ):
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
            splits = headings_processor(segments, headings, heading, level)
                
            split_docs.extend(splits)
            
        documents.extend(split_docs)
        split_docs = []
    
    return documents
                
            

def split_on_heading(document:str, heading_level:int = 2):
    split_headings = []
    document = [document]
        
    for i in range(heading_level):
        split_on = "\n" + "#" * (i+1) + " "
        split_headings.append(split_on)
    
    for level, heading in enumerate(split_headings):
        _logger.debug(f"splitting on: {heading}")
        
        document = document_splitter(heading, document, level)
    
    return document




def get_heading_text(heading_sections:list):

    # latest h1
    h1 = None
    metadata = []

    for heading in heading_sections:
        section_metadata = {}
        if heading.startswith("\n# "):
            h1 = heading.split("\n")[1].strip()
            h1.replace("# ", "")
            section_metadata["h1"] = h1
        else:
            heading.replace("## ", "")
            section_metadata["h1"] = h1
            section_metadata["h2"] = heading.split("\n")[1].strip()

        metadata.append(section_metadata)
        
    return metadata


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    with open("example_source.md", "rb") as f:
        document = f.read()

    h2s = split_on_heading(document.decode("utf-8"), heading_level=2)

    # Get text length
    for h2 in h2s:
        print(len(h2))
    
    for h2 in h2s:
        print("section:   ", h2[0:100])

    metatdata = get_heading_text(h2s)

    print(metatdata)