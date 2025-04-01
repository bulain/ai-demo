from langchain_community.document_loaders import BSHTMLLoader

file_path = "data/bs4-demo.html"
loader = BSHTMLLoader(file_path)
data = loader.load()

print(data)