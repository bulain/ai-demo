from langchain_community.document_loaders import JSONLoader

import json
from pathlib import Path
from pprint import pprint

file_path = 'data/json-demo.json'
data = json.loads(Path(file_path).read_text())
pprint(data)

loader = JSONLoader(
    file_path=file_path,
    jq_schema='.messages[].content',
    text_content=False
    )

data = loader.load()
pprint(data)