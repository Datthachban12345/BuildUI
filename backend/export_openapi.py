import json
from backend.app.main import app

def export_openapi():
    openapi_schema = app.openapi()
    with open("docs/specs/openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    print("Exported docs/specs/openapi.json successfully!")

if __name__ == "__main__":
    export_openapi()
