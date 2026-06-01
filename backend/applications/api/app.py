import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/users")
async def read_users(): ...


@app.post("/users")
async def create_user(): ...


@app.get("/users/{id_}")
async def read_user(id_: int): ...


@app.patch("/users/{id_}")
async def update_user(id_: int): ...


@app.delete("/users/{id_}")
async def delete_user(id_: int): ...


def start():
    uvicorn.run(app=app, host="0.0.0.0", port=8000, reload=True)
