from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.core.config import settings
from app.db.database import connect_to_mongo, close_mongo_connection

app = FastAPI(title=settings.PROJECT_NAME)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Connect to MongoDB on startup and close on shutdown
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

# Include API routes
app.include_router(api_router, prefix=settings.API_STR)

# Ensure that the request is an HTMX request.
def ensure_htmx_request(request: Request):
    if "hx-request" not in request.headers:
        return False
    return True

# Root route
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

# Include routes for pages
@app.get("/login")
async def login_page(request: Request):
    if ensure_htmx_request(request):
        return templates.TemplateResponse("login.html", {"request": request})
    else:
        return RedirectResponse("/", status_code=302)

@app.get("/register")
async def register_page(request: Request):
    if ensure_htmx_request(request):
        return templates.TemplateResponse("register.html", {"request": request})
    else:
        return RedirectResponse("/", status_code=302)

@app.get("/logout")
async def logout_page(request: Request):
    response = templates.TemplateResponse("logout.html", {"request": request})
    response.delete_cookie("DomeToken")
    return response

@app.get("/main")
async def main_page(request: Request):
    if ensure_htmx_request(request):
        return templates.TemplateResponse("main.html", {"request": request})
    else:
        return RedirectResponse("/", status_code=302)

@app.get("/profile")
async def profile_page(request: Request):
    if ensure_htmx_request(request):
        return templates.TemplateResponse("profile.html", {"request": request})
    else:
        return RedirectResponse("/", status_code=302)