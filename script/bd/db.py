
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey,Date,Boolean,String,text
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector 

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, connect_args={"sslmode":"require"})
Base = declarative_base()

class Persona(Base):
    __tablename__ = "persona"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Text)
    apellidos = Column(Text)
    correo = Column(Text)
    contrasena = Column(Text)
    foto = Column(Text)


class Libros(Base):
    __tablename__ = "libros"
    id = Column(Integer, primary_key=True, autoincrement=True)
    libro = Column(Text,nullable=False)
    document_chunks = relationship("DocumentChunks",back_populates="libros", cascade="all, delete-orphan")

class DocumentChunks(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_libro = Column(Integer,ForeignKey("libros.id", ondelete="CASCADE"),nullable=False)
    contenido = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    libros = relationship("Libros", back_populates="document_chunks")




def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    print("✅ Tablas creadas correctamente con pgvector.")

if __name__== "__main__":
    init_db()