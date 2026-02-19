import logging

logger = logging.getLogger(__name__)

def log_api_error(endpoint, error):
    logger.error(f"API Error in {endpoint}: {str(error)}")

def log_api_success(endpoint, status_code):
    logger.info(f"API Success in {endpoint}: {status_code}")