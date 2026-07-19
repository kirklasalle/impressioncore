"""Unit tests for src.core.utils.chunk_large_text."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.utils.chunk_large_text import main


def test_chunk_large_text_main():
    # Mock command line arguments
    test_args = ["chunk_large_text", "dummy_input.txt", "dummy_output_dir", "--strategy", "paragraph"]
    
    # Mock TextChunker
    mock_chunker_instance = MagicMock()
    mock_chunker_instance.chunk_by_paragraphs.return_value = ["chunk 1", "chunk 2"]
    
    # Mock Path methods
    with patch("sys.argv", test_args):
        with patch("src.core.utils.chunk_large_text.TextChunker", return_value=mock_chunker_instance):
            with patch.object(Path, "read_text", return_value="Sample input text content") as mock_read:
                with patch.object(Path, "mkdir") as mock_mkdir:
                    with patch.object(Path, "write_text") as mock_write:
                        main()
                        mock_read.assert_called_once()
                        mock_mkdir.assert_called_once()
                        assert mock_write.call_count == 2
