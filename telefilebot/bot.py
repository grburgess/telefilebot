import asyncio
import logging
from typing import Dict, List

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from .directory import Directory
from .utils.logging import setup_logger

logger = setup_logger(__name__)


class TeleFileBot:
    def __init__(
        self,
        name: str,
        token: str,
        chat_id: str,
        directories: List[Directory],
        wait_time: int,
    ) -> None:
        logger.debug(f"{name} bot is being constructed")
        self._name: str = name
        self._chat_id: str = chat_id
        self._token: str = token
        self._msg_header = ""
        self._directories: List[Directory] = directories
        self._wait_time: int = int(wait_time * 60)  # convert minutes to seconds
        self._application: Application = None

    async def _speak(self, message: str) -> None:
        full_msg = f"{self._msg_header}{message}"
        logger.info(f"{self._name} bot is sending: {message}")
        await self._application.bot.send_message(chat_id=self._chat_id, text=full_msg)

    async def _check_directories(self) -> None:
        for directory in self._directories:
            new_files: Dict[str, str] = directory.check()
            for k, v in new_files.items():
                if v == "new":
                    msg = f"NEW FILE:\n {k}"
                    await self._speak(msg)
                    logger.info(msg)
                elif v == "modified":
                    msg = f"MODIFIED FILE:\n {k}"
                    await self._speak(msg)
                    logger.info(msg)

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Bot is starting up!"
        )

    async def run(self):
        self._application = Application.builder().token(self._token).build()

        # Add command handler
        self._application.add_handler(CommandHandler("start", self.start_command))

        # Start the bot
        await self._application.initialize()
        await self._application.start()
        await self._speak("Starting up!")

        while True:
            try:
                await self._check_directories()
                await asyncio.sleep(self._wait_time)
            except Exception as e:
                logger.error(f"Error: {e}")
                await self._speak("Something went wrong!")
