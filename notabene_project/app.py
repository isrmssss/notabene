from fastapi import FastAPI, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from typing import List, Optional
import database
import ui_builder

app = FastAPI(title="notabene AI")

app.mount("/static", StaticFiles(directory="static"), name="static")

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
async def read_root():
    return HTMLResponse(content=ui_builder.render_index())

# --- Маршруты API для JavaScript ---
@app.get("/api/providers")
async def get_providers():
    return database.get_all_providers()

@app.post("/api/providers")
async def add_provider(provider: ProviderSchema):
    result = database.save_provider_with_models(provider.dict())
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# --- HTMX эндпоинты ---
@app.get("/htmx/providers")
async def htmx_providers():
    """Возвращает HTML фрагмент списка провайдеров"""
    providers = database.get_all_providers()
    return Response(content=ui_builder.render_providers_list(providers))

@app.get("/htmx/provider-form")
async def htmx_provider_form(provider_id: int = None):
    """Возвращает HTML форму для добавления/редактирования провайдера"""
    provider = None
    if provider_id:
        providers = database.get_all_providers()
        provider = next((p for p in providers if p['id'] == provider_id), None)
    return Response(content=ui_builder.render_provider_form(provider))

@app.post("/htmx/providers")
async def htmx_add_provider(
    name: str = Form(...),
    api_key: str = Form(None),
    base_url: str = Form(None),
    model_names: List[str] = Form([]),
    model_codes: List[str] = Form([])
):
    """HTMX POST для сохранения провайдера"""
    # Собираем модели
    models = []
    for name_val, code_val in zip(model_names, model_codes):
        if name_val and code_val:
            models.append({"name": name_val, "model_code": code_val})
    
    # Создаем payload
    payload = {
        "name": name,
        "api_key": api_key if api_key else None,
        "base_url": base_url if base_url else None,
        "models": models
    }
    
    # Сохраняем в БД
    result = database.save_provider_with_models(payload)
    if result["status"] == "error":
        return Response(content=f'<div style="color: red;">Ошибка: {result["message"]}</div>', status_code=400)
    
    # Возвращаем обновленный список провайдеров
    return await htmx_providers()

@app.post("/htmx/chat")
async def htmx_create_chat(chat_name: str = Form(...)):
    """Создает новый чат и возвращает HTML элемент чата"""
    if not chat_name.strip():
        chat_name = "Безымянный блокнот"
    return Response(content=ui_builder.render_chat_item(chat_name))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)