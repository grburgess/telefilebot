from typing import List, Dict
import time
import math
import telegram

from .utils.logging import setup_logger


from .directory import Directory


logger = setup_logger(__name__)


class TeleFileBot:
    def __init__(
        self, name: str, token: str, chat_id: str, directories: List[Directory], wait_time: int
    ) -> None:
        """
        A generic telegram bot

        :param name: the name of the bot
        :param token: the bot token
        :param chat_id: the chat id to talk to
        :returns:
        :rtype:

        """

        logger.debug(f"{name} bot is being constructed")

        # create the bot

        self._name: str = name
        self._chat_id: str = chat_id

        self._bot: telegram.Bot = telegram.Bot(token=token)

        self._msg_header = ""

        self._directories: List[Directory] = directories

        self._wait_time: int = int(math.ceil(60 * wait_time)) # in seconds

    def _speak(self, message: str) -> None:
        """
        send a message

        :param message:
        :returns:
        :rtype:

        """

        full_msg = f"{self._msg_header}{message}"

        logger.info(f"{self._name} bot is sending: {message}")

        self._bot.send_message(chat_id=self._chat_id, text=full_msg)

    # def _show(self, image: str, description: str):
    #     """
    #     send an image

    #     :param image:
    #     :param description:
    #     :returns:
    #     :rtype:

    #     """

    #     full_msg = f"{self._msg_header}{description}"

    #     logger.info(f"{self._name} bot is sending the {description} image")

    #     self._bot.send_photo(
    #         chat_id=self._chat_id, photo=open(image, "rb"), caption=full_msg
        # )

    def _check_directories(self) -> None:

        for directory in self._directories:

            new_files: Dict[str, str] = directory.check()

            for k, v in new_files.items():

                if v == "new":

                    # found a new file
                    msg = f"NEW FILE:\n {k}"

                    self._speak(msg)

                    logger.info(msg)

                elif v == "modified":

                    # foun a modified file

                    msg = f"MODIFIED FILE:\n {k}"

                    self._speak(msg)

                    logger.info(msg)

    def listen(self):


        while True:

            self._check_directories()

            time.sleep(self._wait_time)
