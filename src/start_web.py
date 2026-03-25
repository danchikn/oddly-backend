import uvicorn

from src.api import get_configured_app

app = get_configured_app()

if __name__ == '__main__':
    uvicorn.run(
        app='src.start_web:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )
