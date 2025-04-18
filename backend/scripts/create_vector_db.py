import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_file = os.path.join(project_root, "illness_description.txt")
db_dir = os.path.join(project_root, "chroma_db")

db_drugs = None


def create_embeddings():
    raw_documents = TextLoader(input_file).load()
    text_splitter = CharacterTextSplitter(chunk_size=0, chunk_overlap=0, separator="\n")
    documents = text_splitter.split_documents(raw_documents)

    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Создание и сохранение векторной базы данных
    db_drugs = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory=db_dir  # указываем db_dir для сохранения базы
    )

    print(f"Векторная база данных успешно создана и сохранена в {db_dir}")


if __name__ == "__main__":
    create_embeddings()
