import os

import pytest

current_directory = os.path.dirname(os.path.abspath(__file__))
test_directory = os.path.join(current_directory, "tests")
pytest.main([test_directory, "-v"])
