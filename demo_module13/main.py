"""Small FastAPI app for a one-hour Module 11 demo."""  # File purpose: expose the schema/model demo through a web API.

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException  # FastAPI creates the web application and route decorators.
from app.database import create_tables, get_db
from app.models.calculation import Calculation  # Imports the ORM-style model and factory method.
from app.models.user import User  # Imports the simple demo user model.
from app.schemas.calculation import (  # Imports the Pydantic request/response contracts.
    CalculationRequest,  # Validates incoming JSON before our endpoint logic runs.
    CalculationResponse,  # Shapes the JSON returned back to the client.
)
from app.schemas.user import UserCreate, UserResponse  # Contracts for the demo user routes.

app = FastAPI(title="Minimal Module 12 Demo")  # This is the ASGI app that Uvicorn runs.
demo_users: dict[str, User] = {}  # Small in-memory store so user routes appear in Swagger without a DB.


@app.get("/")  # Registers a GET route for the home page of the API.
def read_root():  # Function that handles GET / requests.
    return {  # FastAPI automatically serializes this dictionary to JSON.
        "message": "Open /docs and try POST /users and POST /calculate.",  # Tells students where to test the API.
        "note": "This demo keeps users and calculations in memory. It does not save to a database yet.",  # Clarifies no DB persistence yet.
    }


@app.post("/users", response_model=UserResponse, status_code=201, tags=["users"])
def create_user(request: UserCreate):
    """Create a simple demo user and keep it in memory."""

    if any(user.username == request.username for user in demo_users.values()):
        raise HTTPException(status_code=400, detail="Username already exists in the demo store.")
    if any(user.email == request.email for user in demo_users.values()):
        raise HTTPException(status_code=400, detail="Email already exists in the demo store.")

    user = User(
        id=str(uuid4()),
        username=request.username,
        email=str(request.email),
        first_name=request.first_name,
        last_name=request.last_name,
        created_at=datetime.now(UTC),
    )
    demo_users[user.id] = user

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        created_at=user.created_at,
        persisted=False,
    )


@app.get("/users", response_model=list[UserResponse], tags=["users"])
def list_users():
    """Return all demo users currently held in memory."""

    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            created_at=user.created_at,
            persisted=False,
        )
        for user in demo_users.values()
    ]


@app.get("/users/{user_id}", response_model=UserResponse, tags=["users"])
def get_user(user_id: str):
    """Return one demo user by id from the in-memory store."""

    user = demo_users.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found in the demo store.")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        created_at=user.created_at,
        persisted=False,
    )


@app.post("/calculate", response_model=CalculationResponse)  # Registers POST /calculate and documents the response model.
def calculate(request: CalculationRequest):  # FastAPI converts and validates request JSON into CalculationRequest.
    """Validate input, create the right calculation class, and return a result."""  # Endpoint purpose for Swagger/docs.

    calculation = Calculation.create(  # Factory method chooses Addition/Subtraction/Multiplication/Division.
        request.type.value,  # Uses the enum's string value, like "addition" or "division".
        request.user_id,  # Carries user ownership data, even though we are not storing it yet.
        request.inputs,  # Passes the validated list of numbers into the model object.
    )
    result = calculation.get_result()  # Polymorphic call: same method name, subclass-specific behavior.

    return CalculationResponse(  # Builds the response object FastAPI will serialize to JSON.
        type=calculation.type,  # Echoes the calculation type used by the model.
        inputs=calculation.inputs,  # Echoes the validated numeric inputs.
        result=result,  # Returns the computed result.
        class_name=type(calculation).__name__,  # Shows which subclass the factory created.
        persisted=False,  # Reminds students this was calculated in memory, not saved to DB.
    )

