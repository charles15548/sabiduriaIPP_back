import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
import numpy as np

from script.lmm.embeddings.embedding import dividir_en_chunks,limpiar_texto,generar_embedding

load_dotenv()


DATABASE_URL=os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL,
                       connect_args={"sslmode": "require"})


def subirLibro(nombre_libro, contenido):
    chunks = dividir_en_chunks(contenido)

    with engine.begin() as conn:
        resultBook = conn.execute(
            text("""
                INSERT INTO libros (libro)
                VALUES (:libro)
                RETURNING id;
            """),
            {
                "libro": nombre_libro,
            }
        )
        bookId = resultBook.scalar()
        query = text("""
            INSERT INTO document_chunks
                (id_libro,contenido, embedding)
            VALUES
                (:id_libro,:contenido, :embedding)
        """)

        for texto in chunks:
            chunk_limpio = limpiar_texto(texto)
            embedding = generar_embedding(chunk_limpio)

            emb = np.array(embedding, dtype=np.float32)

            conn.execute(
                query,{
                    "id_libro": bookId,
                    "contenido": chunk_limpio,
                    "embedding": emb,
                }
            )



        
        
