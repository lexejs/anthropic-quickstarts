"""
Hot reloading runner for Telegram bot
"""

import logging
import os
import select
import subprocess
import sys
import time
from pathlib import Path
from typing import Union

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.should_reload = False
        self.start_bot()

    def on_modified(self, event):
        # Fix for endswith type error - convert to string first
        src_path = str(event.src_path)
        if src_path.endswith('.py'):
            logger.info(f"Detected change in {src_path}")
            self.should_reload = True

    def start_bot(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            time.sleep(0.5)
            logger.info("Stopped previous bot instance")

        try:
            result = subprocess.run(
                ["pgrep", "-f", "computer_use_demo.telegram_bot"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        subprocess.run(["kill", pid])
                        logger.info(f"Killed existing bot process with PID {pid}")
                    except Exception as e:
                        logger.error(f"Failed to kill process {pid}: {e}")
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error checking for existing processes: {e}")

        logger.info("Starting new bot instance")
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'  # Disable Python buffering
        
        self.process = subprocess.Popen(
            [sys.executable, "-m", "computer_use_demo.telegram_bot"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
            env=env
        )
        self.should_reload = False

    def check_output(self):
        if self.process:
            logger.debug("Checking process output...")
            reads = [self.process.stdout, self.process.stderr]
            readable, _, _ = select.select(reads, [], [], 0.01)
            
            if readable:
                logger.debug(f"Got readable fds: {len(readable)}")

            for fd in readable:
                if fd == self.process.stdout:
                    line = fd.readline()
                    if line:
                        print(line.strip(), flush=True)
                elif fd == self.process.stderr:
                    line = fd.readline()
                    if line and 'ERROR' in line:
                        print(line.strip(), file=sys.stderr, flush=True)
                    elif line:
                        print(line.strip(), flush=True)

            # Check process status
            if self.process.poll() is not None:
                logger.error("Bot process died unexpectedly")
                self.start_bot()

    def run(self):
        # Fix for path type in schedule
        path = str(Path(__file__).parent)  # Convert Path to string
        observer = Observer()
        observer.schedule(self, path, recursive=True)
        observer.start()

        try:
            while True:
                if self.should_reload:
                    logger.info("Reloading bot...")
                    self.start_bot()
                self.check_output()
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Stopping bot and observer...")
            if self.process:
                self.process.terminate()
            observer.stop()
            observer.join()

def main():
    """Run bot with hot reload"""
    try:
        logger.info("Starting bot with hot reload")
        reloader = BotReloader()
        reloader.run()
    except Exception as e:
        logger.error(f"Error in hot reload: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 