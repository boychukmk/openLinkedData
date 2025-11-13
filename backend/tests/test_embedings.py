from unittest.mock import patch, MagicMock
import backend.scripts.create_vector_db as cvd

@patch("backend.scripts.create_vector_db.TextLoader.load")
@patch("backend.scripts.create_vector_db.CharacterTextSplitter.split_documents")
@patch("backend.scripts.create_vector_db.HuggingFaceEmbeddings")
@patch("backend.scripts.create_vector_db.Chroma.from_documents")
def test_create_embeddings(mock_chroma, mock_embeddings, mock_splitter, mock_loader):
    mock_loader.return_value = ["doc1", "doc2"]
    mock_splitter.return_value = ["chunk1", "chunk2"]
    mock_embeddings.return_value = "embedding_obj"
    mock_chroma.return_value = MagicMock()

    cvd.create_embeddings()

    mock_loader.assert_called_once()
    mock_splitter.assert_called_once()
    mock_embeddings.assert_called_once_with(model_name="all-MiniLM-L6-v2")
    mock_chroma.assert_called_once_with(
        documents=["chunk1", "chunk2"],
        embedding="embedding_obj",
        persist_directory=cvd.db_dir
    )
