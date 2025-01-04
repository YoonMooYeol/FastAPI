from os import access

from database.orm import ToDo
from database.repository import ToDoRepository, UserRepository
from service.user import UserService
from tests.conftest import client
from database.orm import User


def test_get_todos(client, mocker):
    access_token: str = UserService().create_jwt(username="test")
    headers = {"Authorization": f"Bearer {access_token}"}

    user = User(id=1, username="test", password="hashed")
    user.todos = [
        ToDo(id=1, contents="FastAPI Section 0", is_done=True),
        ToDo(id=2, contents="FastAPI Section 1", is_done=False)
    ]
    mocker.patch.object(
        UserRepository,
        "get_user_by_username",
        return_value=user
    )

    response = client.get("/todos", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
        ]
    }

    response = client.get("/todos?order=DESC", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
        ]
    }

def test_get_todo(client, mocker):
    mocker.patch.object(ToDoRepository,
        "get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="FastAPI Section 0", is_done=True)
    )
    
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "FastAPI Section 0", "is_done": True}

    mocker.patch.object(ToDoRepository,
        "get_todo_by_todo_id",
        return_value=None)

    response = client.get("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail" : "ToDo Not Found"}


def test_create_todo(client, mocker):
    create_spy = mocker.spy(ToDo,"create")
    mocker.patch.object(ToDoRepository,
        "create_todo",
        return_value=ToDo(id=1, contents="todo", is_done=True)
    )

    body = {
        "contents": "test",
        "is_done": False,
    }
    response = client.post("/todos", json=body)
    
    assert response.status_code == 201
    assert response.json() == {"id": 1, "contents": "todo", "is_done": True}
    assert create_spy.spy_return.id is None
    assert create_spy.spy_return.contents == "test"
    assert create_spy.spy_return.is_done is False


def test_update_todo(client, mocker):
    # ToDo 객체를 반환하도록 수정
    mocker.patch.object(ToDoRepository,
        "get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="todo", is_done=True)
    )
    undone = mocker.patch.object(ToDo, "undone")
    # ToDo 객체를 반환하도록 수정
    mocker.patch.object(ToDoRepository,
        "update_todo",
        return_value=ToDo(id=1, contents="todo", is_done=False)
    )

    response = client.patch("/todos/1", json={"is_done": False})

    undone.assert_called_once_with()

    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "todo", "is_done": False}

    mocker.patch.object(ToDoRepository,
        "get_todo_by_todo_id",
        return_value=None)


def test_delete_todo(client, mocker):
    #204
    mocker.patch.object(ToDoRepository,
        "get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="FastAPI Section 0", is_done=True)
    )

    mocker.patch.object(ToDoRepository, "delete_todo", return_value=None)

    response = client.delete("/todos/1")
    assert response.status_code == 204


    #404
    mocker.patch.object(ToDoRepository,
        "get_todo_by_todo_id",
        return_value=None)

    response = client.delete("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "ToDo Not Found"}