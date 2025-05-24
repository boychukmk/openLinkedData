
from backend.sparql_queries import get_drug_illness_graph, get_hospitals_from_wikidata, get_diseases_from_wikidata
import pytest
from unittest.mock import patch, Mock
import requests
from backend import sparql_queries

@patch("backend.sparql_queries.requests.get")
def test_get_diseases_success(mock_get):
    # Імітуємо успішну відповідь з JSON
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": {
            "bindings": [
                {
                    "disease": {"value": "http://www.wikidata.org/entity/Q123"},
                    "diseaseLabel": {"value": "Test Disease"},
                    "description": {"value": "desc"},
                    "icd10": {"value": "A00"},
                    "subclassOfLabel": {"value": "Class1"},
                    "causeLabel": {"value": "Cause1"},
                    "symptomLabel": {"value": "Symptom1"},
                    "fatalityRate": {"value": "0.1"},
                    "diagnosticMethodLabel": {"value": "Method1"},
                    "treatmentLabel": {"value": "Treatment1"},
                    "relatedGeneLabel": {"value": "Gene1"},
                }
            ]
        }
    }
    mock_get.return_value = mock_response

    result = get_diseases_from_wikidata()
    assert len(result) == 1
    disease = result[0]
    assert disease["name"] == "Test Disease"
    assert disease["icd10"] == "A00"
    assert "Cause1" in disease["causes"]
    assert "Symptom1" in disease["symptoms"]

@patch("backend.sparql_queries.requests.get")
def test_get_diseases_http_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_get.return_value = mock_response

    with pytest.raises(Exception) as excinfo:
        get_diseases_from_wikidata()
    assert "Error 500" in str(excinfo.value)

@patch("backend.sparql_queries.requests.get")
def test_get_diseases_json_decode_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)
    mock_get.return_value = mock_response

    with pytest.raises(Exception) as excinfo:
        get_diseases_from_wikidata()
    assert "Ошибка декодирования JSON" in str(excinfo.value)


# --- Тести для get_hospitals_from_wikidata ---

@patch("backend.sparql_queries.SPARQLWrapper.query")
@patch("backend.sparql_queries.SPARQLWrapper.setQuery")
@patch("backend.sparql_queries.SPARQLWrapper.setReturnFormat")
def test_get_hospitals_parsing(mock_setReturnFormat, mock_setQuery, mock_query):
    # Імітуємо результат SPARQL-запиту
    mock_query.return_value.convert.return_value = {
        "results": {
            "bindings": [
                {
                    "hospital": {"value": "http://www.wikidata.org/entity/Q456"},
                    "hospitalLabel": {"value": "Test Hospital"},
                    "geo": {"value": "Point(10 20)"},
                    "hospitalDescription": {"value": "desc"},
                    "website": {"value": "https://example.com"},
                    "wikiImportURL": {"value": "https://import.url"},
                    "image": {"value": "http://commons.wikimedia.org/File:Image.jpg"},
                    "address": {"value": "123 Main St"},
                }
            ]
        }
    }

    hospitals = get_hospitals_from_wikidata("US")
    assert len(hospitals) == 1
    h = hospitals[0]
    assert h["name"] == "Test Hospital"
    assert abs(h["latitude"] - 20.0) < 0.0001
    assert abs(h["longitude"] - 10.0) < 0.0001
    assert h["image"].startswith("https://commons.wikimedia.org/wiki/Special:FilePath/")

# --- Тести для get_drug_illness_graph ---

@patch("backend.sparql_queries.SPARQLWrapper.query")
@patch("backend.sparql_queries.SPARQLWrapper.setQuery")
@patch("backend.sparql_queries.SPARQLWrapper.setReturnFormat")
def test_get_drug_illness_graph_parsing(mock_setReturnFormat, mock_setQuery, mock_query):
    mock_query.return_value.convert.return_value = {
        "results": {
            "bindings": [
                {
                    "item": {"value": "http://example.org/disease1"},
                    "itemLabel": {"value": "Disease1"},
                    "rgb": {"value": "FFA500"},
                    "link": {"value": "http://link.org/disease1"}
                },
                {
                    "item": {"value": "http://example.org/drug1"},
                    "itemLabel": {"value": "Drug1"},
                    "rgb": {"value": "7FFF00"},
                    # link відсутній
                }
            ]
        }
    }

    data = get_drug_illness_graph()
    assert len(data) == 2
    assert data[0]["label"] == "Disease1"
    assert data[0]["color"] == "FFA500"
    assert data[0]["link"] == "http://link.org/disease1"
    assert data[1]["label"] == "Drug1"
    assert data[1]["link"] == ""