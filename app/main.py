from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from app.database import Base, engine
from fastapi.responses import HTMLResponse

# from app.routers import auth_router, user_router, class_router, skill_router, student_router, analytics_router, export_router 

app = FastAPI()

# ... (origins and middleware code is the same)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(auth_router.router)
# app.include_router(user_router.router)
# app.include_router(class_router.router)
# app.include_router(skill_router.router)
# app.include_router(student_router.router)
# app.include_router(analytics_router.router)
# app.include_router(export_router.router)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<h1><h1>It Works!</h1><p>FastAPI is running successfully.</p>"