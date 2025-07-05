import logging
import logging.handlers
from pathlib import Path
from src.config import config

def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup logger with configuration from config.ini"""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    log_config = config.logging_config
    
    # Set log level
    log_level = getattr(logging, log_config['level'].upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = Path(log_config['file'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=log_config['max_size_mb'] * 1024 * 1024,
        backupCount=log_config['backup_count']
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger