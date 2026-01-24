import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
import numpy as np

from script.ml.embeddings.embedding import dividir_en_chunks,limpiar_texto,generar_embedding

load_dotenv()


DATABASE_URL=os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL,
                       connect_args={"sslmode": "require"})


def subirLibro(nombre_libro, paginas):
    
       

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


        TAMAÑO_LOTE = 40

        lote = []
        total_chunks = 0

        for pagina in paginas:
            num_pag = pagina["pagina"]
            texto = pagina["texto"]
            print(f"📄 Procesando página {num_pag}")

            for chunk in dividir_en_chunks(
                 texto
            ):
                chunk_limpio = limpiar_texto(chunk)
                if not chunk_limpio:
                      continue
                embedding = generar_embedding(chunk_limpio)
                if embedding is None:
                    continue

                #emb = np.array(embedding, dtype=np.float32)

                lote.append({
                    "id_libro": bookId,
                    "contenido": chunk_limpio,
                    "embedding": embedding.tolist(),
                    "pagina": num_pag
                })
                total_chunks +=1

                if len(lote) >= TAMAÑO_LOTE:
                    _insertar_lote_embeddings(lote)
                    print(f"💾 Insertados {total_chunks} chunks")
                    lote.clear()
        # 🔹 3. Último remanente
        if lote:
            _insertar_lote_embeddings(lote)
            print(f"💾 Insertados {total_chunks} chunks (final)")

        print("✅ Documento procesado completamente")
        return bookId









    
def _insertar_lote_embeddings(lote: list[dict]):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO document_chunks
                    (id_libro, contenido, embedding, pagina)
                VALUES
                    (:id_libro, :contenido, (:embedding)::vector, :pagina)
            """),
            lote
        )


            
            
def listar_libros():
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                SELECT id, libro
                FROM libros
                ORDER BY id DESC
            """)
        ).fetchall()

    return [
        {
            "id": r.id,
            "nombre_libro": r.libro
        }
        for r in result
    ]



def eliminar_libro(id_libro: int) -> bool:
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                DELETE FROM libros
                WHERE id = :id_libro
            """),
            {"id_libro": id_libro}
        )

    return result.rowcount > 0


def obtener_listado():
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text("SELECT libro FROM libros ORDER BY id ASC")
            ).fetchall()

        return [r.libro for r in result]
    except Exception as e:
        print(f"❌ Error al obtener listado: {e}")
        return []
