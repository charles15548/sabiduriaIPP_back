import os
import numpy as np
from script.ml.embeddings.embedding import generar_embedding  # Usa tu función existente
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
load_dotenv()
# Config DB
VECTORES_CACHE = None
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def select_chunck(pregunta, cantidad_chunks):
    session = SessionLocal()

    try:
        embedding = generar_embedding(pregunta)

        if isinstance(embedding, np.ndarray):
            embedding = [float(x) for x in embedding]

        query = text("""
            SELECT 
                dc.id_libro,
                l.libro AS nombre_libro,
                dc.contenido,
                dc.pagina
            FROM document_chunks dc
            JOIN libros l ON l.id = dc.id_libro
            WHERE trim(coalesce(dc.contenido, '')) <> ''
            ORDER BY dc.embedding <=> (:pregunta)::vector
            LIMIT :cantidad
        """)

        result = session.execute(
            query,
            {
                "pregunta": embedding,
                "cantidad": cantidad_chunks
            }
        ).fetchall()

        if not result:
            return []

        return [
            {
                "contenido": r.contenido,
                "libro": r.nombre_libro,
                "pagina": r.pagina,
                "id_libro": r.id_libro
            }
            for r in result
        ]

    except Exception as e:
        print(f"❌ Error en select_chunck: {e}")
        return []

    finally:
        session.close()











