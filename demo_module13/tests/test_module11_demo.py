from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models.calculation import Addition, Calculation, Division
from app.models.user import User
from app.schemas.calculation import CalculationRequest, CalculationType
from app.schemas.user import UserCreate
from main import calculate, create_user, demo_users, get_user, list_users


@pytest.fixture(autouse=True)
def clear_demo_users():
    demo_users.clear()
    yield
    demo_users.clear()


def test_schema_normalizes_calculation_type():
    data = CalculationRequest(
        type="ADDITION",
        inputs=[1, 2, 3],
        user_id=str(uuid4()),
    )

    assert data.type == CalculationType.ADDITION
    assert data.inputs == [1.0, 2.0, 3.0]


def test_schema_rejects_division_by_zero():
    with pytest.raises(ValidationError, match="Cannot divide by zero"):
        CalculationRequest(
            type="division",
            inputs=[100, 0],
            user_id=str(uuid4()),
        )


def test_factory_returns_correct_subclasses():
    user_id = str(uuid4())

    assert isinstance(Calculation.create("addition", user_id, [1, 2]), Addition)
    assert isinstance(Calculation.create("division", user_id, [1, 2]), Division)


def test_fastapi_calculate_function_uses_polymorphic_model():
    result = calculate(
        CalculationRequest(
            type="multiplication",
            inputs=[2, 3, 4],
            user_id="demo-user-1",
        )
    )

    assert result.model_dump(mode="json") == {
        "type": "multiplication",
        "inputs": [2.0, 3.0, 4.0],
        "result": 24.0,
        "class_name": "Multiplication",
        "persisted": False,
    }


def test_simple_user_model_supports_demo_fields():
    user = User(
        id="demo-user-1",
        username="demo_user",
        email="demo@example.com",
        first_name="Demo",
        last_name="User",
    )

    assert user.id == "demo-user-1"
    assert user.username == "demo_user"
    assert user.email == "demo@example.com"


def test_create_user_route_returns_demo_user():
    result = create_user(
        UserCreate(
            username="demo_user",
            email="demo@example.com",
            first_name="Demo",
            last_name="User",
        )
    )

    assert result.username == "demo_user"
    assert result.email == "demo@example.com"
    assert result.persisted is False


def test_list_and_get_user_routes_use_in_memory_store():
    created = create_user(
        UserCreate(
            username="demo_user",
            email="demo@example.com",
        )
    )

    users = list_users()
    loaded = get_user(created.id)

    assert len(users) == 1
    assert users[0].id == created.id
    assert loaded.username == "demo_user"


def test_create_user_route_rejects_duplicate_username():
    create_user(
        UserCreate(
            username="demo_user",
            email="demo@example.com",
        )
    )

    with pytest.raises(HTTPException, match="Username already exists"):
        create_user(
            UserCreate(
                username="demo_user",
                email="another@example.com",
            )
        )
