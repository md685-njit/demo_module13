"""Minimal SQLAlchemy-style models for the Module 11 demo."""  # File purpose: show model inheritance and polymorphism.

from uuid import uuid4  # Generates unique IDs for model objects.

from sqlalchemy import Column, Float, JSON, String  # SQLAlchemy column types used by the demo model.
from app.models.base import Base  # Shared ORM base so multiple demo models can inherit from one place.

# All SQLAlchemy ORM models inherit from the shared Base in app.models.base.


class Calculation(Base):  # Parent ORM model for all calculation types.
    """Base model. The type column is the polymorphic discriminator."""  # Explains the main inheritance concept.

    __tablename__ = "demo_calculations"  # Name of the table these objects would map to if persisted.

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))  # Unique row/object identifier.
    user_id = Column(String, nullable=False)  # User ownership field for future database persistence.
    type = Column(String(50), nullable=False)  # Discriminator: tells SQLAlchemy which subclass this row represents.
    inputs = Column(JSON, nullable=False)  # Stores a flexible list of numbers, such as [1, 2, 3].
    result = Column(Float, nullable=True)  # Optional computed result; can be filled after calculation.

    __mapper_args__ = {  # SQLAlchemy mapper settings for polymorphic inheritance.
        "polymorphic_on": "type",  # Use the type column to decide which subclass to instantiate.
        "polymorphic_identity": "calculation",  # Identity for the base class itself.
    }

    @classmethod  # Makes this callable as Calculation.create(...) without an instance.
    def create(cls, calculation_type: str, user_id: str, inputs: list[float]):  # Factory method inputs.
        """Return the correct calculation subclass for the requested type."""  # Factory purpose.

        calculation_classes = {  # Maps incoming type strings to concrete Python classes.
            "addition": Addition,  # "addition" should create an Addition object.
            "subtraction": Subtraction,  # "subtraction" should create a Subtraction object.
            "multiplication": Multiplication,  # "multiplication" should create a Multiplication object.
            "division": Division,  # "division" should create a Division object.
        }

        normalized_type = calculation_type.lower()  # Makes the factory tolerant of uppercase/lowercase input.
        calculation_class = calculation_classes.get(normalized_type)  # Looks up the matching subclass.

        if calculation_class is None:  # Handles unsupported types like "modulus".
            raise ValueError(f"Unsupported calculation type: {calculation_type}")  # Fails clearly for invalid types.

        return calculation_class(  # Creates and returns the specific subclass object.
            user_id=user_id,  # Passes through user ownership information.
            type=normalized_type,  # Stores the discriminator value on the object.
            inputs=inputs,  # Stores the validated numbers on the object.
        )

    def get_result(self) -> float:  # Shared method name that subclasses must implement.
        raise NotImplementedError("Subclasses must implement get_result().")  # Prevents using the base class directly.


class Addition(Calculation):  # Subclass representing addition calculations.
    __mapper_args__ = {"polymorphic_identity": "addition"}  # SQLAlchemy identity for addition rows/objects.

    def get_result(self) -> float:  # Addition-specific implementation of the shared method.
        return sum(self.inputs)  # Adds all numbers in the inputs list.


class Subtraction(Calculation):  # Subclass representing subtraction calculations.
    __mapper_args__ = {"polymorphic_identity": "subtraction"}  # SQLAlchemy identity for subtraction rows/objects.

    def get_result(self) -> float:  # Subtraction-specific implementation of the shared method.
        result = self.inputs[0]  # Starts with the first number.
        for value in self.inputs[1:]:  # Loops through every remaining number.
            result -= value  # Subtracts each remaining number from the running result.
        return result  # Returns the final subtraction result.


class Multiplication(Calculation):  # Subclass representing multiplication calculations.
    __mapper_args__ = {"polymorphic_identity": "multiplication"}  # SQLAlchemy identity for multiplication rows/objects.

    def get_result(self) -> float:  # Multiplication-specific implementation of the shared method.
        result = 1  # Starts at 1 because 1 is the multiplicative identity.
        for value in self.inputs:  # Loops through every input number.
            result *= value  # Multiplies the running result by the current number.
        return result  # Returns the final multiplication result.


class Division(Calculation):  # Subclass representing division calculations.
    __mapper_args__ = {"polymorphic_identity": "division"}  # SQLAlchemy identity for division rows/objects.

    def get_result(self) -> float:  # Division-specific implementation of the shared method.
        result = self.inputs[0]  # Starts with the first number as the numerator.
        for value in self.inputs[1:]:  # Loops through remaining numbers as denominators.
            if value == 0:  # Protects the model method if zero somehow reaches this layer.
                raise ValueError("Cannot divide by zero.")  # Raises a clear domain error.
            result /= value  # Divides the running result by the current denominator.
        return result  # Returns the final division result.
