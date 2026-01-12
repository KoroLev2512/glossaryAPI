import json
from pathlib import Path

from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from app.main import app

OUTPUT_DIR = Path("static_docs")
OUTPUT_DIR.mkdir(exist_ok=True)

schema = get_openapi(
    title=app.title,
    version=app.version,
    routes=app.routes,
)

openapi_path = OUTPUT_DIR / "openapi.json"
openapi_path.write_text(json.dumps(schema, indent=2))

# Generate standalone HTML pointing to local openapi.json
swagger_html = get_swagger_ui_html(openapi_url="openapi.json", title="Swagger UI").body.decode()
redoc_html = get_redoc_html(openapi_url="openapi.json", title="ReDoc").body.decode()

(OUTPUT_DIR / "swagger.html").write_text(swagger_html)
(OUTPUT_DIR / "redoc.html").write_text(redoc_html)

print(f"Wrote {openapi_path.resolve()}")
print(f"Wrote {(OUTPUT_DIR / 'swagger.html').resolve()}")
print(f"Wrote {(OUTPUT_DIR / 'redoc.html').resolve()}")
