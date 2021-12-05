from fastapi import FastAPI

from app.controllers import security, routers

app = FastAPI()
app.include_router(routers.router)
app.include_router(security.router)


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}
