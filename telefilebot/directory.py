from pathlib import Path
from typing import Optional, List, Dict

from .utils.logging import setup_logger


log = setup_logger(__name__)


class Directory:
    def __init__(self, path, extensions=None, recursion_limit=None):

        self._path: Path = Path(path).expanduser().absolute()

        # make sure the recursion_limit is at least 0
        if recursion_limit is not None:

            if recursion_limit < 0:

                log.error(
                    f"trying to set a recursion limit less than zero in {path}"
                )

        self._recursion_limit: Optional[int] = recursion_limit

        self._extensions: Optional[List[str]] = extensions

        self._known_files: Dict[str, float] = {}

        log.info(f"Created a watch in {self._path}")

        if self._recursion_limit is not None:

            log.info(f"with a recursion limit of {self._recursion_limit}")

        if self._extensions is not None:

            for ext in self._extensions:

                log.info(f" searching for extension {ext}")

        # now look for the initial set of files
        log.info("Initalizing the file list")

        initial_files = self._descend_directory(self._path, current_depth=0)

        for k, v in initial_files.items():

            self._known_files[k] = v

            log.info(f"inital file: {k}")

    def _descend_directory(
        self, path: Path, current_depth: int
    ) -> Dict[str, float]:
        """
        recursively descend a directory until a recursion limit is
        reached and return all the files needed

        """
        collected_files: Dict[str, float] = {}

        log.debug(f"checking dir {path} at a depth of {current_depth}")

        for x in path.iterdir():

            if x.is_file():

                extension = x.suffix

                if self._extensions is not None:

                    # if this is not what we are looking for

                    if extension not in self._extensions:

                        continue

                # ok, this is something we want to keep
                # so record when it was modified

                collected_files[
                    str(x.relative_to(self._path))
                ] = x.stat().st_mtime

            elif x.is_dir():

                if self._recursion_limit is not None:

                    if current_depth + 1 > self._recursion_limit:

                        continue

                # ok we will descend the directory

                sub_files: Dict[str, float] = self._descend_directory(
                    x, current_depth=current_depth + 1
                )

                for k, v in sub_files.items():

                    collected_files[k] = v

        return collected_files

    def check(self) -> Dict[str, str]:
        """
        Check the current directory against the known file list.
        Returns a dictionary mapping filenames to their change type: "new", "modified", or "deleted"
        """

        changes: Dict[str, str] = {}

        new_listings: Dict[str, float] = self._descend_directory(
            self._path, current_depth=0
        )

        # Check for new and modified files
        for k, v in new_listings.items():

            # first check the known files and
            # see if one of these has been modified
            # since the last check

            if k in self._known_files:

                # compare the times

                if self._known_files[k] < v:

                    # this file has been modified

                    changes[k] = "modified"

                    # now lets update the time
                    # in the original list

                    log.debug(
                        f"{k} is moving its time from {self._known_files[k]} to {v}"
                    )

                    self._known_files[k] = v

            else:

                # this is a new file

                changes[k] = "new"

                # lets add it to the known list

                self._known_files[k] = v

                log.debug(f"updated the known file list with {k}")

        # Check for deleted files
        deleted_files = set(self._known_files.keys()) - set(new_listings.keys())

        for deleted_file in deleted_files:
            changes[deleted_file] = "deleted"
            log.debug(f"file deleted: {deleted_file}")

            # Remove from known files
            del self._known_files[deleted_file]

        log.debug(f"finished checking {self._path}")

        return changes
