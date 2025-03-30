from decouple import config
from llama_index.core.data_structs import Node
from llama_index.core.schema import NodeWithScore
from llama_index.postprocessor.dashscope_rerank import DashScopeRerank

nodes = [
    NodeWithScore(node=Node(text="text1"), score=0.70),
    NodeWithScore(node=Node(text="text2"), score=0.75),
    NodeWithScore(node=Node(text="text3"), score=0.80),
    NodeWithScore(node=Node(text="text4"), score=0.85),
    NodeWithScore(node=Node(text="text5"), score=0.90),
]

dashscope_rerank = DashScopeRerank(top_n=3, model="gte-rerank",api_key=config("ALI_API_KEY"))
results = dashscope_rerank.postprocess_nodes(nodes, query_str="<user query>")
for res in results:
    print("Text: ", res.node.get_content(), "Score: ", res.score)
