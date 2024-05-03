import os
from llama_index.core.storage import StorageContext
from llama_index.core.indices.loading import load_index_from_storage
from llama_index.core import VectorStoreIndex
from llama_index.readers.file import PDFReader
from llama_index.core import SimpleDirectoryReader


def get_index(data, index_name):
    index = None
    if not os.path.exists(index_name):
        print("building index", index_name)
        index = VectorStoreIndex.from_documents(data, show_progress=True)
        index.storage_context.persist(persist_dir=index_name)
    else:
        index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=index_name)
        )

    return index


reader = SimpleDirectoryReader(
    input_files=["./data/postflop_guide1.txt","./data/postflop_guide2.txt","./data/postflop_guide3.txt"]
)

docs = reader.load_data()

poker_index = get_index(docs, "postflop_eng")
postflop_engine = poker_index.as_query_engine()
