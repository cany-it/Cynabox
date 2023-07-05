from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import Union
import uvicorn
import httpx
import logging
import os

class BodyReq(BaseModel):
    container: Union[str, None] = None
    timeout: Union[float, None] = 30

class CTIApi:

    def init(self):
        self.app = FastAPI(
            title="CTI Api",
            description="Fast API"
        )

        @self.app.post("/alive")
        async def isup():
            return {'message': 'FastApi is up'}

        @self.app.post("/run")
        async def forward_request(request_body: BodyReq):
            try:
                os.system(f'docker run {request_body.container}')
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Error: {e}") from e
            
        @self.app.post("/run")
        async def forward_request(request_body: BodyReq):
            try:
                os.system(f'docker run - {request_body.container}')
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Error: {e}") from e

        @self.app.post("/image")
        async def image(request_body: BodyReq):
            try:
                os.system(f'docker images | grep {request_body.container} > DockerPs.txt')
                image_name = request_body.container
                with open("DockerPs.txt") as f:
                    lines = f.readlines()
                    for line in lines:
                        if image_name in line:
                            os.system(f'docker rmi {image_name}')
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Error: {e}") from e

    
    def run(self):
        uvicorn.run(self.app, host='0.0.0.0', port=9999)

api = CTIApi()
api.init()
api.run()