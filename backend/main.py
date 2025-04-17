from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.sparql_queries import get_diseases_from_wikidata, get_hospitals_from_wikidata, get_drug_illness_graph
from backend.llm_adviser import get_illness_and_drugs

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/diseases")
def get_diseases():
    return get_diseases_from_wikidata()


class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
def chat(request: ChatRequest):
    response_text = get_illness_and_drugs(request.message, top_k=10)

    return {"reply": response_text}


@app.get("/api/hospitals")
def get_hospitals(country: str = "Q212"):
    return get_hospitals_from_wikidata(country)


@app.get("/api/drug-disease")
async def get_drug_disease_data():
    return get_drug_illness_graph()
