# -*- coding: utf-8 -*-
import logging
import sys
from .config_loader import load_config

config = load_config()
log_level = getattr(logging, config["LOG_LEVEL"], logging.INFO)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)

def get_logger(name):
    return logging.getLogger(name)