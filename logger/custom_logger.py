# cutomer_logger.py
from datetime import datetime
import logging
import os
import structlog

class CustomLogger:
    def __init__(self):
        # Ensure logs directory exists
        self.logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)

        # Timestamped log file (for persistence)
        log_file = f"{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, log_file)

        logging.basicConfig(
            filename=self.log_file_path,
            level=logging.INFO,
            format="[ %(asctime)s ] %(levelname)s %(name)s (line:%(lineno)d) - %(message)s",
        )

    def get_logger(self, name=__file__ ):

        return logging.getLogger(os.path.basename(name))

        # logger_name = os.path.basename(name)

        # # Configure logging for console + file (both JSON)
        # file_handler = logging.FileHandler(self.log_file_path)
        # file_handler.setLevel(logging.INFO)
        # file_handler.setFormatter(logging.Formatter('%(message)s'))

        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.INFO)
        # console_handler.setFormatter(logging.Formatter('%(message)s'))

        # logging.basicConfig(
        #     handlers=[file_handler, console_handler],
        #     level=logging.INFO,
        #     format='%(message)s', # Structlog will handle JSON formatting
        # )

        # # Configure structlog for JSON structured logging
        # structlog.configure(
        #     processors = [
        #         structlog.processors.TimeStamper(fmt = "iso", utc=True, key = "timestamp"),
        #         structlog.processors.add_log_level,
        #         structlog.processors.EventRenamer(to="event"),
        #         structlog.processors.JSONRenderer()
        #     ],
        #     logger_factory = structlog.stdlib.LoggerFactory(),
        #     cache_logger_on_first_use=True,
        # )

        # return structlog.get_logger(logger_name)
    

# --- Usage Example ---
if __name__ == "__main__":
    logger=CustomLogger()
    logger=logger.get_logger(__file__)
    logger.info("Custom logger initialized.")
    
    # logger = CustomLogger().get_logger(__file__)
    # logger.info("User uploaded a file", user_id=123, filename="report.pdf")
    # logger.error("Failed to process PDF", error="File not found", user_id=123)

