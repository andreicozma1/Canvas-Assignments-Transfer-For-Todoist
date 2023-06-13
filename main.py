"""
Modifications by Andrei Cozma which are based on the original code from the following repository:
- https://github.com/scottquach/Canvas-Assignments-Transfer-For-Todoist

What's new:
 - Use the 'canvasapi' library instead of requests for shorter/cleaner code
 - Use the 'pick' library for better multiple-item selection
 - Added ability to rename a course as it appears as a Todoist project (can optionally use the default name from Canvas)
 - Automatically set task priority based on keywords (configurable)
 - Print short and detailed summaries after assignment transfer.
 - Shows counts of new assignments, updated assignments, and skipped assignments (already submitted or already up to date)
 - Optional file downloading capability
 - Reformatted print statements for better verbosity and readability.
"""

import argparse
import logging
import os
import traceback

from src.CanvasFileDownloader import CanvasFileDownloader
from src.CanvasToTodoist import CanvasToTodoist
from src.helpers.LogHelper import notify
from src.Utils import setup

os_save_path, config_path, log_path = setup()


def setup_logging():
    # Set up logging
    log_handlers = [logging.FileHandler(log_path, mode="w"), logging.StreamHandler()]
    logging.basicConfig(
        level=logging.INFO,
        # level=logging.INFO,
        format="%(message)s",
        # format="%(asctime)s %(levelname)6s : %(message)s [%(funcName)s():%(lineno)s]",
        handlers=log_handlers,
    )


def main():

    # Parse arguments and extract boolean flag -y which defaults to false
    parser = argparse.ArgumentParser(
        description="Transfer Canvas assignments to Todoist"
    )
    parser.add_argument(
        "-t", "--todoist", action="store_true", help="Run CanvasToTodoist"
    )
    parser.add_argument(
        "-f", "--files", action="store_true", help="Run CanvasFileDownloader"
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Run both CanvasToTodoist and CanvasFileDownloader",
    )
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompts"
    )
    parser.add_argument("--reset", action="store_true", help="Reset config file")
    parser.add_argument("-e", "--edit", action="store_true", help="Edit config file")
    parser.add_argument("--logs", action="store_true", help="Show logs")

    args = parser.parse_args()
    skip_confirmation_prompts = args.yes

    if args.edit:
        # Open in default editor
        os.system(f"${{EDITOR:-vi}} \"{config_path}\"")
        exit(0)

    if args.logs:
        # Open in default editor
        os.system(
            f"less {log_path} || cat {log_path} || open {log_path} || xdg-open {log_path}"
        )
        exit(0)

    if not any([arg in ["-t", "-f", "-a"] for arg in os.sys.argv]):
        # print help if no arguments are provided
        parser.print_help()
        parser.error("Must have either -t, -f, or -a")

    setup_logging()
    logging.info(f"Logs saved to: {log_path}")
    logging.info("")

    if skip_confirmation_prompts:
        logging.info("Skipping confirmation prompts")

    try:
        if args.todoist or args.all:
            CanvasToTodoist(args, config_path, skip_confirmation_prompts).run()
            logging.info("")
        if args.files or args.all:
            CanvasFileDownloader(
                args, config_path, os_save_path, skip_confirmation_prompts
            ).run()
            logging.info("")
    except KeyboardInterrupt:
        logging.info("Exiting...")
        exit(0)
    except Exception as e:
        notify("Canvas-Sync Exception", str(e))
        raise e


if __name__ == "__main__":
    # Main Execution
    main()
