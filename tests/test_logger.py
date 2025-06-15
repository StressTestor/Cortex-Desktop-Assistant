"""Tests for the logger module."""

import logging
import os
import tempfile
from pathlib import Path

import pytest

from logger import get_logger, setup_logging


def test_get_logger():
    """Test that get_logger returns a logger with the correct name."""
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"


def test_logger_level():
    """Test that the logger respects the log level."""
    logger = get_logger("test_logger_level")
    
    # Default level should be INFO
    assert logger.level == logging.INFO
    
    # Change level and verify
    logger.setLevel(logging.DEBUG)
    assert logger.level == logging.DEBUG


def test_log_file_creation():
    """Test that log files are created in the specified directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        
        # Setup logging with the temp log file
        setup_logging(log_file=log_file, log_level=logging.DEBUG)
        
        # Get a logger and log a message
        logger = get_logger("test_log_file")
        test_message = "This is a test log message"
        logger.info(test_message)
        
        # Flush the logger to ensure the message is written to disk
        for handler in logger.handlers:
            handler.flush()
        
        # Verify the log file was created and contains the message
        assert log_file.exists()
        log_content = log_file.read_text()
        assert test_message in log_content


def test_log_format():
    """Test that the log format is correct."""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "format_test.log"
        
        # Setup logging with the temp log file
        setup_logging(log_file=log_file, log_level=logging.INFO)
        
        # Get a logger and log a message
        logger = get_logger("test_log_format")
        test_message = "Format test message"
        logger.info(test_message)
        
        # Flush the logger to ensure the message is written to disk
        for handler in logger.handlers:
            handler.flush()
        
        # Read the log file
        log_content = log_file.read_text()
        
        # Check the log format (simplified check)
        assert "INFO" in log_content
        assert "test_log_format" in log_content
        assert test_message in log_content


def test_multiple_loggers():
    """Test that multiple loggers work independently."""
    logger1 = get_logger("logger1")
    logger2 = get_logger("logger2")
    
    assert logger1.name == "logger1"
    assert logger2.name == "logger2"
    assert logger1 is not logger2
