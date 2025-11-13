import pytest
import pandas as pd
from backend.sparql_queries import (
    get_diseases_from_wikidata,
    get_hospitals_from_wikidata
)
from backend.llm_adviser import get_illness_and_drugs


def test_get_illness_and_drugs_without_drugs():
    result = get_illness_and_drugs("diabetes", top_k=3, get_drugs=False)
    assert isinstance(result, pd.DataFrame)
    assert 'medical_condition' in result.columns
    assert len(result) > 0


from unittest.mock import MagicMock
import pandas as pd

def test_get_illness_and_drugs_with_drugs(dummy_drugs_df, monkeypatch):
    # Замінюємо датафрейм
    monkeypatch.setattr("backend.llm_adviser.drugs_df", dummy_drugs_df)

    # Мокаємо результат similarity_search
    mock_doc = MagicMock()
    mock_doc.page_content = "treatment Info: This is some mock info"
    mock_db = MagicMock()
    mock_db.similarity_search.return_value = [mock_doc]

    monkeypatch.setattr("backend.llm_adviser.db_drugs", mock_db)

    # Виклик функції
    result = get_illness_and_drugs("treatment", top_k=2, get_drugs=True)

    # Перевірки
    assert isinstance(result, pd.DataFrame)
    assert 'name' in result.columns
    assert len(result) > 0



def test_get_diseases_from_wikidata_structure():
    result = get_diseases_from_wikidata()
    assert isinstance(result, list)
    assert len(result) > 0
    disease = result[0]
    expected_keys = {
        'id', 'name', 'url', 'description', 'icd10', 'subclass_of',
        'causes', 'symptoms', 'fatality_rate', 'diagnostic_methods',
        'treatments', 'related_genes'
    }
    assert expected_keys.issubset(disease.keys())


@pytest.mark.parametrize("country_code", ["Q30", "Q40", "Q183"])
def test_get_hospitals_from_wikidata(country_code):
    hospitals = get_hospitals_from_wikidata(country_code)
    assert isinstance(hospitals, list)
    assert len(hospitals) > 0
    first = hospitals[0]
    assert "name" in first
    assert "latitude" in first
    assert "longitude" in first
    assert "description" in first
