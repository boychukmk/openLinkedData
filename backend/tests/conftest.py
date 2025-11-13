import pytest
import pandas as pd

@pytest.fixture
def dummy_drugs_df():
    return pd.DataFrame({
        'name': ['DrugA', 'DrugB'],
        'description': ['Used for treatment A', 'Used for treatment B'],
        'rating': [4.5, 3.9],
        "medical_condition": ["treatment", "treatment"],
        "medical_condition_description": ["Info about treatment A", "Info about treatment B"]
    })
