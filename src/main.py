from fastapi import FastAPI
from api import todo, user, email
import uvicorn


app = FastAPI()
app.include_router(todo.router)
app.include_router(user.router)
app.include_router(email.router)


@app.get("/")
def health_check_handler():
    return {"안녕하세요. 정상적으로 실행되었습니다.": "api를 테스트 하려면 url뒤쪽에 /docs를 입력하세요."}


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)


