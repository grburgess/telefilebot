import pytest
import time
from pathlib import Path

from telefilebot.directory import Directory
from telefilebot.utils.logging import update_logging_level


update_logging_level("DEBUG")


def test_directory(test_dir):


    d = Directory(path=test_dir, recursion_limit=None, extensions=None)

    p = Path(test_dir)


    assert "file.txt" in d._known_files

    new_file = p / "test.f"

    new_file.touch()


    d.check()

    assert "test.f" in d._known_files


    new_dir = p / "one" / "two"

    new_dir.mkdir(parents=True)

    new_file2 = new_dir / "help.txt"

    new_file2.touch()

    d.check()

    assert "one/two/help.txt" in d._known_files


    old_time = d._known_files["file.txt"]

    time.sleep(5)

    with (p / "file.txt").open("w") as f:

        f.write("testing")



    d.check()

    new_time = d._known_files["file.txt"]

    assert new_time > old_time



def test_directory_ext(test_dir):


    d = Directory(path=test_dir, recursion_limit=1, extensions=[".txt"])

    p = Path(test_dir)


    assert "file.txt" in d._known_files

    new_file = p / "test.f"

    new_file.touch()


    d.check()

    assert "test.f" not in d._known_files


    new_dir = p / "one" / "two"

    new_dir.mkdir(parents=True)

    new_file2 = new_dir / "help.txt"

    new_file2.touch()

    d.check()

    assert  "one/two/help.txt" not in d._known_files


    old_time = d._known_files["file.txt"]

    time.sleep(5)

    with (p / "file.txt").open("w") as f:

        f.write("testing")




    d.check()

    new_time = d._known_files["file.txt"]

    assert new_time > old_time
