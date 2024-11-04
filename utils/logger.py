import logging


def setup_logging():
    """Настраивает логирование"""
    logging.basicConfig(
        filename="app.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
