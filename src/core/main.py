from dotenv import load_dotenv
load_dotenv()
import logging
import os
import uvicorn
from src.core.interface.server import create_fastapi_app

def main():
    level = os.getenv("LOGGER_LEVEL", logging.INFO)
  
    logging.basicConfig(
        level=int(level),
        format="%(levelname)s - %(name)s - %(message)s"
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)

    
    logger = logging.getLogger(__name__)
    app = create_fastapi_app()

    logger.debug("!!!!! LOGGER LEVEL SET TO DEBUG !!!!!")
    
    port = os.getenv("PORT", 8000)
    concurrency_limit = os.getenv("CONCURRENCY_LIMIT", 100)
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=int(port),
        workers=1,
        access_log=False,  
        limit_concurrency=concurrency_limit,  
        timeout_keep_alive=30
    )

if __name__ == "__main__":
    main()
    
    