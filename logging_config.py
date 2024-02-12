import logging

def configure_logger():
    logging.basicConfig(level=logging.INFO, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = logging.FileHandler('errors.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    logging.getLogger().addHandler(file_handler)

