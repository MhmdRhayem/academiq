from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.schemas import GradeInput, GradePrediction, HealthResponse, ModelInfo
from app.predictor import predictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    predictor.load_model()
    yield


app = FastAPI(
    title="Student Grade Predictor API",
    description="Predict S5-S6 course grades based on S1-S4 performance",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        model_loaded=predictor.is_loaded,
        model_name=predictor.model_name if predictor.is_loaded else None
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        model_loaded=predictor.is_loaded,
        model_name=predictor.model_name if predictor.is_loaded else None
    )


@app.get("/model/info", response_model=ModelInfo)
async def get_model_info():
    if not predictor.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")

    info = predictor.get_model_info()
    return ModelInfo(**info)


@app.post("/predict", response_model=GradePrediction)
async def predict_grades(input_data: GradeInput):
    if not predictor.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        predictions, model_name = predictor.predict(input_data.grades)
        return GradePrediction(predictions=predictions, model_used=model_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/courses/input")
async def get_input_courses():
    if not predictor.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"courses": predictor.feature_columns}


@app.get("/courses/output")
async def get_output_courses():
    if not predictor.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"courses": predictor.target_columns}