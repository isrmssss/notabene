from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import database

app = FastAPI(title="notabene AI")

# Подключаем статику и шаблоны
# Обязательно убедись, что папки "static" и "templates" созданы в корне проекта!
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Инициализация БД при старте приложения
database.init_db()

# --- Схемы валидации данных (Pydantic) ---
class ModelSchema(BaseModel):
    name: str          # Понятное имя для юзера (напр. "GPT-4o")
    model_code: str    # Технический код (напр. "gpt-4o-2024-05-13")

class ProviderSchema(BaseModel):
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[ModelSchema] = []

# --- Маршруты страниц ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Контекст должен быть ОДНИМ словарем, где ключ "request" строго обязателен
    return templates.TemplateResponse("index.html", {"request": request})

# --- Маршруты API ---
@app.get("/api/providers")
async def get_providers():
    return database.get_all_providers()

@app.post("/api/providers")
async def add_provider(provider: ProviderSchema):
    result = database.save_provider_with_models(provider.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

if __name__ == "__main__":
    import uvicorn
    # ИСПРАВЛЕНО: Комментарий изменен на Python-style (# вместо //)
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)