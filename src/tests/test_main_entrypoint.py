"""Unit tests for the main CLI entrypoint (src/main.py)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch
import pytest

from src import main


class TestMainCli:
    """Tests for the main CLI functionality in main.py."""

    @patch("src.main.argparse.ArgumentParser.print_help")
    def test_main_no_args(self, mock_print_help):
        """No command prints help and returns 0."""
        with patch.object(sys, "argv", ["main.py"]):
            exit_code = main.main_cli_entry()
            assert exit_code == 0
            mock_print_help.assert_called_once()

    @patch("src.main.init_api")
    @patch("src.main.handle_tokenize")
    def test_main_tokenize_command(self, mock_handle_tokenize, mock_init_api):
        """Tokenize command triggers handle_tokenize."""
        mock_api = MagicMock()
        mock_init_api.return_value = mock_api
        mock_handle_tokenize.return_value = 0

        with patch.object(sys, "argv", ["main.py", "tokenize", "--content", "hello"]):
            exit_code = main.main_cli_entry()
            assert exit_code == 0
            mock_init_api.assert_called_once()
            mock_handle_tokenize.assert_called_once()

    @patch("src.main.init_api")
    @patch("src.main.handle_detokenize")
    def test_main_detokenize_command(self, mock_handle_detokenize, mock_init_api):
        """Detokenize command triggers handle_detokenize."""
        mock_api = MagicMock()
        mock_init_api.return_value = mock_api
        mock_handle_detokenize.return_value = 0

        with patch.object(sys, "argv", ["main.py", "detokenize", "--modality", "text", "--input-file", "tokens.bin"]):
            exit_code = main.main_cli_entry()
            assert exit_code == 0
            mock_init_api.assert_called_once()
            mock_handle_detokenize.assert_called_once()

    @patch("src.main.init_api")
    @patch("src.main.define_model_from_config")
    def test_main_define_model_command(self, mock_define_model, mock_init_api):
        """Define model command triggers define_model_from_config."""
        mock_api = MagicMock()
        mock_init_api.return_value = mock_api
        mock_define_model.return_value = {"model_name": "TestModel", "version": "1.0"}

        with patch.object(sys, "argv", ["main.py", "define_model", "--config", "arch.yaml"]):
            exit_code = main.main_cli_entry()
            assert exit_code == 0
            mock_init_api.assert_called_once()
            mock_define_model.assert_called_once()

    @patch("src.main.init_api")
    @patch("src.main.start_training")
    def test_main_train_model_command(self, mock_start_training, mock_init_api):
        """Train model command triggers start_training."""
        mock_api = MagicMock()
        mock_init_api.return_value = mock_api
        mock_start_training.return_value = True

        with patch.object(sys, "argv", ["main.py", "train_model", "--config", "train.yaml"]):
            exit_code = main.main_cli_entry()
            assert exit_code == 0
            mock_init_api.assert_called_once()
            mock_start_training.assert_called_once()

    @patch("src.main.init_api")
    @patch("src.main.start_evaluation")
    def test_main_evaluate_model_command(self, mock_start_evaluation, mock_init_api):
        """Evaluate model command triggers start_evaluation."""
        mock_api = MagicMock()
        mock_init_api.return_value = mock_api
        mock_start_evaluation.return_value = True

        with patch.object(sys, "argv", ["main.py", "evaluate_model", "--config", "eval.yaml"]):
            exit_code = main.main_cli_entry()
            assert exit_code == 0
            mock_init_api.assert_called_once()
            mock_start_evaluation.assert_called_once()
