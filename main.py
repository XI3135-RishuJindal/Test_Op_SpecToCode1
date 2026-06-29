"""Entry-point: run the Flask development server."""

from app.factory import create_app

app = create_app()

if __name__ == "__main__":
    import os

    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_ENV", "production") == "development",
    )
