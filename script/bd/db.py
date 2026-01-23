
import os
from dotenv import load_dotenv
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey,Date,Boolean,String,text
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector 

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Persona(Base):
    __tablename__ = "persona"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Text)
    apellidos = Column(Text)
    correo = Column(Text)
    contrasena = Column(Text)
    foto = Column(Text)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    print("✅ Tablas creadas correctamente con pgvector.")

if __name__== "__main__":
    init_db()