from langchain_community.document_loaders.csv_loader import CSVLoader

file_path = (
    "./cvs-demo.csv"
)

print("<========================>")
loader = CSVLoader(file_path=file_path)
data = loader.load()
for record in data[:2]:
    print("------------------------")
    print(record)

print("<========================>")
loader = CSVLoader(
    file_path=file_path,
    csv_args={
        "delimiter": ",",
        "quotechar": '"',
        "fieldnames": ["description", "script", "installed_by"],
    },
)
data = loader.load()
for record in data[:2]:
    print("------------------------")
    print(record)

print("<========================>")
loader = CSVLoader(file_path=file_path, source_column="script")
data = loader.load()
for record in data[:2]:
    print("------------------------")
    print(record)
