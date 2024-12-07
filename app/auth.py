from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from starlette.status import HTTP_403_FORBIDDEN

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment variables
API_KEY = os.getenv("API_KEY")
# Define the API key header security scheme
api_key_header = APIKeyHeader(name="access_token", auto_error=False)


# Verify the API key in request header
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
