from langserve import RemoteRunnable

remote_chain = RemoteRunnable("http://localhost:8000/chain/")
response = remote_chain.invoke({"language": "中文", "text": "上海有哪些985大学"})

print(response)