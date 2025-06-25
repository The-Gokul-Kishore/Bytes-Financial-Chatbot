import base64
import threading

# import faiss
from pathlib import Path

import camelot
import fitz  # PyMuPDF
import pandas as pd
from bytes.database.db import DBManager
from bytes.retriver.PostgresDocStore import PostgresDocStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.schema.document import Document
from langchain_community.vectorstores.pgvector import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
class Retriver:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Retriver, cls).__new__(cls)
                    cls._instance.__init__()
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "vectorstore"):
            return
        self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db_instance = DBManager()
        self.vectorstore = PGVector(
            connection_string=self.db_instance.db_url,
            collection_name="multi_modal_rag",
            embedding_function=self.embedding_function,
        )
        self.docstore = PostgresDocStore(db_manager=self.db_instance)
        self.retriever = MultiVectorRetriever(
            vectorstore=self.vectorstore, docstore=self.docstore, id_key="doc_id"
        )

    def extract_tables_by_page(self, load_path: Path, doc_name: str):
        pagewise_tables = {}
        for i in range(1, fitz.open(load_path).page_count + 1):
            page_tables = camelot.read_pdf(
                str(load_path), flavor="stream", pages=str(i)
            )
            if len(page_tables) == 0:
                page_tables = camelot.read_pdf(
                    str(load_path), flavor="lattice", pages=str(i)
                )
            table_texts = []
            for table in page_tables:
                if table.df is None:
                    continue
                print(table.df)

                df = table.df.apply(
                    lambda col: col.map(
                        lambda x: x.strip() if isinstance(x, str) else x
                    )
                )
                df = (
                    df.replace(["", "nan", "NaN", "NULL"], pd.NA)
                    .dropna(how="all")
                    .fillna("")
                )
                table_texts.append(df.to_string(index=False, header=True))

            if table_texts:
                pagewise_tables[i] = "\n\n".join(table_texts)

        return pagewise_tables

    def extract_images_by_page(self, doc, doc_name):
        image_b64_by_page = {}
        for i, page in enumerate(doc):
            print(f"Extracting image from page {i+1}")
            pix = page.get_pixmap()
            image_b64 = base64.b64encode(pix.tobytes("jpeg")).decode("utf-8")
            image_b64_by_page[i + 1] = image_b64
        return image_b64_by_page

    def build_combined_pagewise_docs(
        self, doc, doc_name: str, table_map: dict, image_map: dict,thread_id:int=0,
    ):
        documents = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "]
        )
        for i, page in enumerate(doc):
            print("Processing page", i + 1)
            page_num = i + 1
            text = page.get_text()
            tables = table_map.get(page_num, "")

            chunks = text_splitter.split_text(text)
            for j,chunk in enumerate(chunks):
                if(len(chunk.strip("\n").strip(" "))<1):
                    continue
                metadata = {
                "doc_id": f"{doc_name}_page_{page_num}_chunk_{j}",
                "page_number": page_num,
                "doc_name": doc_name,
                "thread_id":thread_id
                }
                print("page;",page_num,"chunk:",j,"content:",chunk)
                documents.append(Document(page_content=chunk, metadata=metadata))
            if(tables):
                for k, table in enumerate(tables):
                    if(len(table.strip("\n").strip(" "))>1):
                        print(table,"k:",k,"page_num:",page_num)
                        documents.append(Document(
                            page_content=f"---TABLE---\n{table}",
                            metadata={
                                "doc_id": f"{doc_name}_page_{page_num}_table_{k}",
                                "page_number": page_num,
                                "table_number": k,
                                "doc_name": doc_name,
                                "thread_id": thread_id
                            }
                        ))
        print(len(documents))
        return documents
    def batch_add_documents(self, documents, batch_size=50):
        print(len(documents))

        for i in range(0, len(documents), batch_size):
            if(documents[i:i+batch_size]==[]):
                continue
            print("i:",i)
            batch = documents[i:i+batch_size]

            print(f"Inserting batch {i} - {i + batch_size}...")
            self.vectorstore.add_documents(batch)

    def parse(self, load_path: Path,  thread_id:int=0):
        doc = fitz.open(str(load_path))
        doc_name = load_path.stem

        table_map = self.extract_tables_by_page(load_path, doc_name)
        image_map = self.extract_images_by_page(doc, doc_name)
        combined_docs = self.build_combined_pagewise_docs(
            doc, doc_name, table_map, image_map,thread_id=thread_id
        )

        self.batch_add_documents(combined_docs)

        self.docstore.mset(
            [(doc.metadata["doc_id"], doc.page_content) for doc in combined_docs]
        )

        # print("\n✅ All pages processed and indexed as unified per-page chunks.")
        # docs = self.retriever.invoke("What is the revenue of the company in FY23?")
        # print("📄 Retrieved documents:", docs)
    def delete_vectorstore(self):
        print("Deleting all data from vectorsotre database...")
        if_delete:bool =  bool(input("Are you sure? (1/0)"))
        if(if_delete):
            self.vectorstore.delete(delete_all=True)

    def retrive(self,query:str,thread_id:int=0,k:int=10):
        return self.retriever.vectorstore.similarity_search(query, k=k,filter={"thread_id":thread_id})
if __name__ == "__main__":
    parser = Retriver()
    parser.parse(
        load_path=Path("C://Users//GOKUL//Downloads//annual-report-2023-2024.pdf"),
    )
