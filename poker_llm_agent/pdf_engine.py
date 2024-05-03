import os
from llama_index.core.storage import StorageContext
from llama_index.core.indices.loading import load_index_from_storage
from llama_index.core import VectorStoreIndex
# from llama_index.readers import PDFReader
# from llama_index.core.readers import pdf_reader as PDFReader
# from llama_index.core.readers import SimpleDirectoryReader
from llama_index.readers.file import PDFReader


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


# pdf_path = os.path.join("data", "poker_guide.pdf")
pdf_path = "./data/poker_wiki.pdf"
# pdf_path = "./data/poker_guide.pdf"
poker_pdf = PDFReader().load_data(file=pdf_path)
# poker_pdf = SimpleDirectoryReader().load_data(pdf_path)
poker_index = get_index(poker_pdf, "poker")
poker_engine = poker_index.as_query_engine()
