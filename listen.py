import click
from click.termui import prompt

from telefilebot import TeleFileBot, read_input_file
from telefilebot.utils.logging import update_logging_level
from telefilebot.utils.read_input_file import InputFile
from telefilebot.directory import Directory
from telefilebot.utils.logging import setup_logger


log = setup_logger(__name__)


@click.command()
@click.option("--file", help="The input file to start the bot")
def listen(file: str) -> None:

    parameters: InputFile = read_input_file(file)

    update_logging_level(parameters.logging.level)

    dirs = []

    # gather the directories

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


    try:

        bot.listen()

    except:

        log.error("EXITING")
