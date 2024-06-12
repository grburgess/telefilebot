import asyncio

import click

from telefilebot import TeleFileBot, read_input_file
from telefilebot.directory import Directory
from telefilebot.utils.logging import setup_logger, update_logging_level
from telefilebot.utils.read_input_file import InputFile

log = setup_logger(__name__)


@click.command()
@click.option("--file", help="The input file to start the bot")
def listen(file: str) -> None:
    parameters: InputFile = read_input_file(file)
    update_logging_level(parameters.logging.level)

    dirs = []

    # Gather the directories
    for directory, params in parameters.directories.items():
        tmp = Directory(
            path=directory,
            extensions=params.extensions,
            recursion_limit=params.recursion_limit,
        )
        dirs.append(tmp)

    bot = TeleFileBot(
        name=parameters.name,
        token=parameters.token,
        chat_id=parameters.chat_id,
        directories=dirs,
        wait_time=parameters.wait_time,
    )

    async def run_bot():
        try:
            await bot.listen()
        except Exception as e:
            log.error(f"EXITING due to error: {e}")

    asyncio.run(run_bot())
