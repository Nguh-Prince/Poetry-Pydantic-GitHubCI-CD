from .database import SessionLocal, engine, Base

from app import create_app

app = create_app()

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    app.run(debug=True)
