from app.__main__ import create_app
from app.api.routes import get_api_router

app = create_app()
app.include_router(get_api_router())
