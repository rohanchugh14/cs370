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
    input_files=["./data/poker_hands.csv"]
)

docs = reader.load_data()

poker_index = get_index(docs, "hand_eng")
hand_engine = poker_index.as_query_engine(response_mode="compact")


# qa_template = (
#     "Context information is below.\n"
#     "---------------------\n"
#     "{context_str}\n"
#     "---------------------\n"
#     "Given the context information and not prior knowledge, "
#     "answer the query (of hole cards and community cards) with the best poker hand it makes.\n"
#     "Query: {query_str}\n"
#     "Answer: "
# )
# hand_engine.update_prompts({"response_synthesizer:text_qa_template": qa_template})

