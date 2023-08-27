import os
import pytest

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Run all tests in the tests directory
pytest.main([current_directory])
