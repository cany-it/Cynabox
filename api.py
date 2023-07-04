from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import uvicorn
import httpx
import logging
import os

class BodyReq(BaseModel):
    command: str
    timeout: float | None = 30

class CTIApi:

    def init(self):
        self.app = FastAPI(
            title="CTI Api",
            description="Fast API"
        )

        @self.app.get("/isup")
        async def isup():
            return {'message': 'FastApi is up'}

        @self.app.post("/command")
        async def forward_request(request_body: BodyReq):
            try:
                async with httpx.AsyncClient(timeout=request_body.timeout) as client:
                    logging.debug(f"Request body: {request_body}")
                    data ={"command": f"{request_body.command}"}
                    
                    os.system(request_body.command)
                    response.raise_for_status()
                    logging.debug(f"Response from second API: {response.json()}")
                    return response.json()
            except httpx.HTTPError as e:
                logging.error(f"HTTP Error: {e}")
                raise HTTPException(status_code=500, detail=f"Error: {e}") from e

    
    def run(self):
        uvicorn.run(self.app, host='0.0.0.0', port=9000)

api = CTIApi()
api.init()
api.run()