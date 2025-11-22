from typing import List, Dict, Tuple
import time
import math
import telegram
from telegram.error import TelegramError, RetryAfter, TimedOut, NetworkError
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        :param directories: list of directories to monitor
        :param wait_time: wait time in minutes between checks
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

        # Rate limiting: track message timestamps (Telegram allows ~30 msg/sec, but we'll be conservative)
        self._message_timestamps: List[float] = []
        self._rate_limit_window = 1.0  # 1 second window
        self._max_messages_per_window = 20  # Max 20 messages per second

    def _rate_limit_check(self) -> None:
        """
        Implement rate limiting to avoid hitting Telegram's limits
        """
        current_time = time.time()

        # Remove timestamps outside the window
        self._message_timestamps = [
            ts for ts in self._message_timestamps
            if current_time - ts < self._rate_limit_window
        ]

        # If we're at the limit, wait
        if len(self._message_timestamps) >= self._max_messages_per_window:
            sleep_time = self._rate_limit_window - (current_time - self._message_timestamps[0])
            if sleep_time > 0:
                logger.debug(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
                # Clean up old timestamps after sleeping
                current_time = time.time()
                self._message_timestamps = [
                    ts for ts in self._message_timestamps
                    if current_time - ts < self._rate_limit_window
                ]

        # Record this message
        self._message_timestamps.append(current_time)

    def _escape_markdown_v2(self, text: str) -> str:
        """
        Escape special characters for Telegram MarkdownV2
        """
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text

    def _speak(self, message: str, use_markdown: bool = True) -> None:
        """
        Send a message with retry logic and rate limiting

        :param message: the message to send
        :param use_markdown: whether to use MarkdownV2 formatting
        :returns:
        :rtype:

        """

        full_msg = f"{self._msg_header}{message}"

        logger.info(f"{self._name} bot is sending: {message}")

        # Retry logic with exponential backoff
        max_retries = 3
        retry_delay = 1  # Start with 1 second

        for attempt in range(max_retries):
            try:
                # Rate limiting
                self._rate_limit_check()

                # Send message
                if use_markdown:
                    self._bot.send_message(
                        chat_id=self._chat_id,
                        text=full_msg,
                        parse_mode='MarkdownV2'
                    )
                else:
                    self._bot.send_message(chat_id=self._chat_id, text=full_msg)

                # Success!
                return

            except RetryAfter as e:
                # Telegram asked us to wait
                wait_time = e.retry_after
                logger.warning(f"Telegram rate limit hit, waiting {wait_time}s")
                time.sleep(wait_time)

            except (TimedOut, NetworkError) as e:
                # Network issues - retry with backoff
                if attempt < max_retries - 1:
                    logger.warning(f"Network error on attempt {attempt + 1}/{max_retries}: {e}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to send message after {max_retries} attempts: {e}")
                    raise

            except TelegramError as e:
                # Other Telegram errors
                logger.error(f"Telegram error: {e}")
                raise

            except Exception as e:
                # Unexpected errors
                logger.error(f"Unexpected error sending message: {e}", exc_info=True)
                raise

    def _check_single_directory(self, directory: Directory) -> Dict[str, str]:
        """
        Check a single directory for changes

        :param directory: the directory to check
        :returns: dictionary of file changes
        """
        try:
            return directory.check()
        except Exception as e:
            logger.error(f"Error checking directory {directory._path}: {e}", exc_info=True)
            return {}

    def _check_directories(self) -> None:
        """
        Check all directories for changes, with parallel processing and batched notifications
        """
        all_changes: List[Tuple[str, str]] = []

        # Check directories in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=min(len(self._directories), 5)) as executor:
            # Submit all directory checks
            future_to_dir = {
                executor.submit(self._check_single_directory, directory): directory
                for directory in self._directories
            }

            # Collect results as they complete
            for future in as_completed(future_to_dir):
                directory = future_to_dir[future]
                try:
                    new_files: Dict[str, str] = future.result()

                    # Collect all changes
                    for filepath, change_type in new_files.items():
                        all_changes.append((filepath, change_type))

                except Exception as e:
                    logger.error(f"Error processing directory {directory._path}: {e}", exc_info=True)

        # If there are changes, batch them into a single message
        if all_changes:
            # Group by change type
            new_files = []
            modified_files = []
            deleted_files = []

            for filepath, change_type in all_changes:
                escaped_path = self._escape_markdown_v2(filepath)

                if change_type == "new":
                    new_files.append(f"    `{escaped_path}`")
                    logger.info(f"NEW FILE: {filepath}")
                elif change_type == "modified":
                    modified_files.append(f"    `{escaped_path}`")
                    logger.info(f"MODIFIED FILE: {filepath}")
                elif change_type == "deleted":
                    deleted_files.append(f"    `{escaped_path}`")
                    logger.info(f"DELETED FILE: {filepath}")

            # Build the message with visual formatting
            msg_parts = []

            # Header
            total_changes = len(all_changes)
            escaped_name = self._escape_markdown_v2(self._name)
            msg_parts.append(f"📁 *{escaped_name}* detected {total_changes} change{'s' if total_changes > 1 else ''}")
            msg_parts.append("━━━━━━━━━━━━━━━━━━━━")

            if new_files:
                count = len(new_files)
                msg_parts.append(f"✨ *New* \\({count}\\)\n" + "\n".join(new_files))

            if modified_files:
                count = len(modified_files)
                msg_parts.append(f"📝 *Modified* \\({count}\\)\n" + "\n".join(modified_files))

            if deleted_files:
                count = len(deleted_files)
                msg_parts.append(f"🗑 *Deleted* \\({count}\\)\n" + "\n".join(deleted_files))

            # Send the batched message
            full_message = "\n\n".join(msg_parts)
            self._speak(full_message, use_markdown=True)

    def listen(self):
        """
        Main loop that monitors directories for changes
        """

        escaped_name = self._escape_markdown_v2(self._name)
        dir_count = len(self._directories)
        wait_mins = self._wait_time / 60

        startup_msg = (
            f"🟢 *{escaped_name}* is now online\\!\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📂 Monitoring *{dir_count}* director{'ies' if dir_count > 1 else 'y'}\n"
            f"⏱ Check interval: *{wait_mins:.0f}* min"
        )
        self._speak(startup_msg, use_markdown=True)

        while True:

            try:

                self._check_directories()

                time.sleep(self._wait_time)

            except TelegramError as e:
                error_msg = self._escape_markdown_v2(str(e))
                logger.error(f"Telegram error in main loop: {e}", exc_info=True)
                try:
                    self._speak(f"⚠️ *Telegram Error*\n`{error_msg}`", use_markdown=True)
                except Exception:
                    # If we can't send the error message, just log it
                    logger.error("Failed to send error notification")
                # Continue monitoring
                time.sleep(5)

            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                try:
                    shutdown_msg = (
                        f"🔴 *{escaped_name}* is shutting down\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"👋 Goodbye\\!"
                    )
                    self._speak(shutdown_msg, use_markdown=True)
                except Exception:
                    pass
                break

            except Exception as e:
                error_msg = self._escape_markdown_v2(str(e))
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                try:
                    self._speak(f"⚠️ *Unexpected Error*\n`{error_msg}`", use_markdown=True)
                except Exception:
                    # If we can't send the error message, just log it
                    logger.error("Failed to send error notification")
                # Continue monitoring
                time.sleep(5)
