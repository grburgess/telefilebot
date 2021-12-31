import logging
import os
import shutil
from glob import glob
from pathlib import Path

import pytest



@pytest.fixture(scope="function")
def test_dir():


    test_path = "test"

    p = Path(test_path)

    p.mkdir()

    p2 = p / "file.txt"

    p2.touch()


    yield test_path




    shutil.rmtree(test_path)
