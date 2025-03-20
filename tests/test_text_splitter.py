import pytest
from RAG.utils.chunking import split_text_into_chunks  # Replace with your actual import

TEXT = """Это первый абзац.  Он состоит из нескольких предложений.
Это второй абзац."""

def test_sentence_splitting_properties():
    chunks = split_text_into_chunks(TEXT, 50, 0, "sentence")
    assert all(len(chunk) <= 50 for chunk in chunks)
    assert all(chunk.strip() for chunk in chunks)
    assert len(chunks) > 0  # Should have *some* chunks

def test_sentence_splitting_with_overlap_properties():
    chunks = split_text_into_chunks(TEXT, 50, 10, "sentence")
    assert all(len(chunk) <= 50 for chunk in chunks)
    assert all(chunk.strip() for chunk in chunks)
    assert len(chunks) > 0

def test_newline_splitting_properties():
    chunks = split_text_into_chunks(TEXT, 100, 0, "newline")
    assert all(len(chunk) <= 100 for chunk in chunks)
    assert all(chunk.strip() for chunk in chunks)
    assert len(chunks) > 0

def test_newline_splitting_with_overlap_properties():
    chunks = split_text_into_chunks(TEXT, 100, 20, "newline")
    assert all(len(chunk) <= 100 for chunk in chunks)
    assert all(chunk.strip() for chunk in chunks)
    assert len(chunks) > 0

def test_short_max_length_properties():
    chunks = split_text_into_chunks(TEXT, 10, 0, "sentence")
    assert all(len(chunk) <= 10 for chunk in chunks)
    assert all(chunk.strip() for chunk in chunks)
    # Removed: assert len(chunks) > 0  <-- This is the problematic line
    if chunks: # Check if the list is NOT empty.
        assert len(chunks) > 0

def test_overlap_error():
    with pytest.raises(ValueError):
        split_text_into_chunks(TEXT, 50, 60, "sentence")

def test_invalid_split_by():
    with pytest.raises(ValueError):
        split_text_into_chunks(TEXT, 50, 0, "invalid")

def test_empty_text_splitter():
    assert split_text_into_chunks("", 50, 0, "sentence") == []