from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import pandas as pd

from backend.scripts.create_dataset import drugs_df


def initialize_db():
    raw_documents = TextLoader("illness_description.txt").load()  # Загружаем документы
    text_splitter = CharacterTextSplitter(chunk_size=0, chunk_overlap=0, separator="\n")
    documents = text_splitter.split_documents(raw_documents)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    db_drugs = Chroma.from_documents(
        documents,
        embedding=embeddings
    )
    return db_drugs


db_drugs = None
if db_drugs is None:
    db_drugs = initialize_db()


def get_illness_and_drugs(query: str, top_k: int = 5, get_drugs: bool = False) -> pd.DataFrame:

    docs = db_drugs.similarity_search(query, k=top_k)
    found_conditions = set(doc.page_content.split(" Info:")[0].strip() for doc in docs)

    if not get_drugs:
        unique_conditions = sorted(list(found_conditions))
        return pd.DataFrame({'medical_condition': unique_conditions})

    query_conditions = [cond for cond in found_conditions if
                        cond.lower() in query.lower() or query.lower() in cond.lower()]

    if query_conditions:
        recommendations = drugs_df[drugs_df['medical_condition'].isin(query_conditions)]
        recommendations = recommendations.sort_values(by='rating', ascending=False)
        return recommendations
    else:
        recommendations = drugs_df[drugs_df['medical_condition'].isin(found_conditions)]
        recommendations = recommendations.sort_values(by='rating', ascending=False)
        return recommendations
