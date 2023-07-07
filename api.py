from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union
import uvicorn
import httpx
import logging
import os


class BodyReq(BaseModel):
    container: Union[str, None] = None
    command: Union[str, None] = None
    params: Union[str, None] = None
    timeout: Union[float, None] = 30

class SCANApi:

    def init(self):
        self.app = FastAPI(
            title="Scan Api",
            description="Fast API"
        )

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        def add_middleware():
            return

        @self.app.post("/alive")
        async def isup(request_body: BodyReq):
            line = "Down"
            try:
                os.system("docker ps | grep %s | awk '{ print $7 }' > isUp.txt" %request_body.container)
                with open("isUp.txt") as f:
                    for line in f:
                        print(line)
                return {line}
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Error {e} ") from e
                
        @self.app.post("/run")
        async def forward_request(request_body: BodyReq):
            try:
                if request_body.command == 'openvas':
                    script_python = "create_openvas_scan.py"
                    target = request_body.params 
                    os.system(f'python3 {script_python} {target}')

            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Error: {e}") from e

        @self.app.post("/run")
        async def forward_request(request_body: BodyReq):
            try:
                os.system(f'docker run --rm {request_body.container}')
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Error: {e}") from e

        @self.app.post("/image")
        async def image(request_body: BodyReq):
            try:
                os.system("docker images | grep %s | awk '{ print $3 }' > DockerPs.txt" %request_body.container)
                image_name = request_body.container
                with open("DockerPs.txt") as f:
                    lines = f.readlines()
                    for line in lines:
                        os.system(f'docker rmi {image_name}')
            except httpx.HTTPError as e:
                raise HTTPException(status_code=500, detail=f"Error: {e}") from e

    def run(self):
        uvicorn.run(self.app, host='localhost', port=9999)

api = SCANApi()
api.init()
api.run()