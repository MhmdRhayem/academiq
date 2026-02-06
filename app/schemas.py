from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional


class GradeInput(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grades": {
                    "M1100": 75.0,
                    "M1101": 80.0,
                    "M1102": 70.0,
                    "PHYS100": 65.0,
                    "PHYS101": 72.0,
                    "I1100": 78.0,
                    "P1101": 68.0,
                    "S1101": 74.0,
                    "P1100": 71.0,
                    "M1103": 76.0
                }
            }
        }
    )

    grades: Dict[str, float] = Field(
        ...,
        description="Dictionary of course codes to grades (S1-S4 courses)"
    )


class GradePrediction(BaseModel):
    predictions: Dict[str, float] = Field(
        ...,
        description="Predicted grades for S5-S6 courses"
    )
    model_used: str = Field(
        ...,
        description="Name of the model used for prediction"
    )


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: Optional[str] = None


class ModelInfo(BaseModel):
    model_name: str
    input_courses: List[str]
    output_courses: List[str]
    metrics: Dict[str, float]