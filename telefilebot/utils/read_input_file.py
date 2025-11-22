from typing import Optional, List, Dict, Union
from omegaconf import OmegaConf
from dataclasses import dataclass, field
from enum import IntEnum
import logging


# logging
class LoggingLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class Logging:
    level: LoggingLevel = LoggingLevel.INFO


@dataclass
class DirectoryListing:

    recursion_limit: Optional[int] = None
    extensions: Optional[List[str]] = None


@dataclass
class InputFile:

    name: str = "telebot"
    token: str = ""
    chat_id: str = ""
    directories: Dict[str, DirectoryListing] = field(default_factory=lambda: {})
    logging: Logging = field(default_factory=Logging)
    wait_time: float = 1  # minute


def read_input_file(file_name: str) -> InputFile:

    base_input: InputFile = InputFile()

    user_input = OmegaConf.load(file_name)

    final_input = OmegaConf.merge(base_input, user_input)

    return final_input
