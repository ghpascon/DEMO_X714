from fastapi.templating import Jinja2Templates
from datetime import datetime
from app.core.path import get_path

def generate_footer():
    year = datetime.now().year
    return f"© {year} - SMARTX"


templates = Jinja2Templates(directory=get_path("app/templates"))
templates.env.globals["generate_footer"] = generate_footer
