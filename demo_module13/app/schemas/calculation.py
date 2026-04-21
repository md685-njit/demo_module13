"""Minimal Pydantic schemas for the Module 11 demo."""  # File purpose: define API data validation contracts.

from enum import Enum  # Enum lets us define a fixed set of valid operation names.

from pydantic import BaseModel, Field, field_validator, model_validator  # Pydantic tools for schema validation.


class CalculationType(str, Enum):  # String enum so values serialize naturally as JSON strings.
    """The operation names our calculator supports."""  # Explains the purpose of this enum in docs/readability.

    ADDITION = "addition"  # Valid operation value for addition.
    SUBTRACTION = "subtraction"  # Valid operation value for subtraction.
    MULTIPLICATION = "multiplication"  # Valid operation value for multiplication.
    DIVISION = "division"  # Valid operation value for division.


class CalculationRequest(BaseModel):  # Pydantic model for incoming POST /calculate JSON.
    """Incoming request data for one calculation."""  # Short description for readers and generated docs.

    type: CalculationType  # Requires the operation to be one of the enum values above.
    inputs: list[float] = Field(..., min_length=2)  # Requires at least two numeric inputs.
    user_id: str  # Represents the user who would own this calculation in a real DB flow.

    @field_validator("type", mode="before")  # Runs before Pydantic converts the value into CalculationType.
    @classmethod  # Pydantic field validators are commonly class methods.
    def normalize_type(cls, value):  # Receives the raw "type" value from incoming JSON.
        if not isinstance(value, str):  # Rejects non-string operation types early.
            raise ValueError("Calculation type must be a string.")  # Clear error for bad type input.
        return value.lower()  # Allows "ADDITION" or "Addition" by normalizing to lowercase.

    @field_validator("inputs", mode="before")  # Runs before Pydantic converts list items to floats.
    @classmethod  # Keeps the validator attached to the schema class.
    def require_list(cls, value):  # Receives the raw "inputs" value from incoming JSON.
        if not isinstance(value, list):  # Rejects strings, numbers, or objects as invalid inputs.
            raise ValueError("Inputs must be a list.")  # Gives students a clear validation message.
        return value  # Lets Pydantic continue validating and converting each item to float.

    @model_validator(mode="after")  # Runs after individual fields have been validated.
    def prevent_division_by_zero(self):  # Checks a rule that depends on both type and inputs.
        if self.type == CalculationType.DIVISION:  # Only applies the zero-denominator rule to division.
            if any(value == 0 for value in self.inputs[1:]):  # Skips first number because it is the numerator.
                raise ValueError("Cannot divide by zero.")  # Stops invalid division before model logic runs.
        return self  # Returns the validated object when all cross-field rules pass.


class CalculationResponse(BaseModel):
    """Response data returned by the FastAPI endpoint."""

    id: str
    user_id: str
    type: CalculationType
    inputs: list[float]
    result: float
    class_name: str
    persisted: bool = False

