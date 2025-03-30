"""
https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql
将此文件保存为Chinook_Sqlite.sql
运行sqlite3 Chinook.db
运行.read Chinook_Sqlite.sql
测试SELECT * FROM Artist LIMIT 10;
"""

from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///Chinook.db")
print(db.dialect)
print(db.get_usable_table_names())
print(db.run("SELECT * FROM Artist LIMIT 10;"))

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from decouple import config

# 初始化模型
llm = init_chat_model(model="deepseek-chat", model_provider="deepseek", api_key=config("DS_API_KEY"))


# 表名列表
class Table(BaseModel):
    """Table in SQL database."""

    name: str = Field(description="Name of table in SQL database.")


table_names = "\n".join(db.get_usable_table_names())
system = f"""Return the names of ALL the SQL tables that MIGHT be relevant to the user question. \
The tables are:

{table_names}

Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed."""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{input}"),
    ]
)
llm_with_tools = llm.bind_tools([Table])
output_parser = PydanticToolsParser(tools=[Table])

print(prompt)
category_chain = prompt | llm_with_tools | output_parser

response = category_chain.invoke({"input": "What are all the genres of Alanis Morisette songs"})
print(response)

# get tables
from typing import List


def get_tables(categories: List[Table]) -> List[str]:
    tables = []
    for category in categories:
        if category.name == "Music":
            tables.extend(
                [
                    "Album",
                    "Artist",
                    "Genre",
                    "MediaType",
                    "Playlist",
                    "PlaylistTrack",
                    "Track",
                ]
            )
        elif category.name == "Business":
            tables.extend(["Customer", "Employee", "Invoice", "InvoiceLine"])
    return tables


table_chain = category_chain | get_tables
response = table_chain.invoke({"input": "What are all the genres of Alanis Morisette songs"})
print(response)

# 组装SQL
from langchain.chains import create_sql_query_chain
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter

query_chain = create_sql_query_chain(llm, db)
table_chain = {"input": itemgetter("question")} | table_chain
full_chain = RunnablePassthrough.assign(table_names_to_use=table_chain) | query_chain

query = full_chain.invoke(
    {"question": "What are all the genres of Alanis Morisette songs"}
)
print(query)
