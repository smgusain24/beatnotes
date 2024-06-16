import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from application.users.views import router as users_router
from application.editor.views import router as editor_router

app = FastAPI()

app.include_router(users_router)
app.include_router(editor_router)


@app.get("/health")
def health():
    return JSONResponse(content={'msg': 'Server is running fine'}, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app)