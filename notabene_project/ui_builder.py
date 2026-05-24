import os

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_TEMPLATES_DIR = os.path.join(_PROJECT_DIR, "templates")
_COMPONENTS_DIR = os.path.join(_TEMPLATES_DIR, "components")

_cache = {}

def _load(path):
    if path not in _cache:
        with open(path, "r", encoding="utf-8") as f:
            _cache[path] = f.read()
    return _cache[path]

def _component(name):
    return _load(os.path.join(_COMPONENTS_DIR, name))


def render_index():
    return _load(os.path.join(_TEMPLATES_DIR, "index.html"))


def render_providers_list(providers):
    if not providers:
        return _component("empty_providers.html")

    card = _component("provider_card.html")
    return "".join(
        card.format(
            provider_id=p["id"],
            name=p["name"],
            models_count=len(p.get("models", [])),
        )
        for p in providers
    )


def render_provider_form(provider=None):
    is_edit = provider is not None

    title = "Редактировать провайдера" if is_edit else "Новый провайдер"
    provider_name = provider["name"] if is_edit else ""
    api_key = provider.get("api_key", "") if is_edit else ""
    base_url = provider.get("base_url", "") if is_edit else ""
    models = provider.get("models", []) if is_edit else []
    disabled_attr = 'disabled' if is_edit else ""

    row = _component("model_row.html")
    if models:
        models_html = "".join(
            row.format(name=m["name"], model_code=m["model_code"])
            for m in models
        )
    else:
        models_html = row.format(name="", model_code="")

    form = _component("provider_form.html")
    return form.format(
        title=title,
        name=provider_name,
        api_key=api_key,
        base_url=base_url,
        disabled_attr=disabled_attr,
        models_html=models_html,
    )


def render_chat_item(chat_name):
    return _component("chat_item.html").format(chat_name=chat_name)
