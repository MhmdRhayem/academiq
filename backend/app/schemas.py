from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional


class GradeInput(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grades": {
                    "M1100": 80.0,
                    "M1101": 80.0,
                    "M1102": 80.0,
                    "PHYS100": 80.0,
                    "PHYS101": 80.0,
                    "I1100": 80.0,
                    "P1101": 80.0,
                    "S1101": 80.0,
                    "P1100": 80.0,
                    "M1103": 80.0,
                    "M1104": 80.0,
                    "M1105": 80.0,
                    "M1106": 80.0,
                    "M1107": 80.0,
                    "I1101": 80.0,
                    "I2202": 80.0,
                    "I2204": 80.0,
                    "I2205": 80.0,
                    "M2251": 80.0,
                    "M2250": 80.0,
                    "I2201": 80.0,
                    "I2203": 80.0,
                    "S2250": 80.0,
                    "I2206": 80.0,
                    "I2207": 80.0,
                    "I2208": 80.0,
                    "I2209": 80.0,
                    "I2210": 80.0,
                    "I2211": 80.0,
                    "I2234": 80.0
                }
            }
        }
    )

    grades: Dict[str, float] = Field(
        ...,
        description="Dictionary of course codes to grades. All 30 S1-S4 courses required for accurate predictions. Missing courses default to 50.0."
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