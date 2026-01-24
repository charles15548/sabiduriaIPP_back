from script.controllers.personas import login

from fastapi import FastAPI, HTTPException,Form,File,Body,UploadFile
from fastapi.responses import JSONResponse
from script.ml.embeddings.subir_libro import procesarSubida
from script.controllers.libro import eliminar_libro, listar_libros
from script.ml.response import response_stream
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List,Literal
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from dotenv import load_dotenv
load_dotenv()
app = FastAPI(title="API RAG")

origins = [
    "http://localhost:3000",              
    "https://soporte2.intelectiasac.com", 
    "https://ipp.intelectiasac.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mensaje(BaseModel):
    rol: Literal["user","bot"]
    contenido: str

class PreguntaEntrada(BaseModel):
    pregunta: str
    historial: List[Mensaje]



@app.post("/consultar-stream")
def consultar_stream(pregunta_entrada: PreguntaEntrada):
    try:
        
        pregunta = pregunta_entrada.pregunta
        historial = pregunta_entrada.historial

        response = response_stream(pregunta,historial)

        return StreamingResponse(response(), media_type="text/event-stream")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))







@app.post("/acceso")
async def log(
correo: str = Form(...),
contrasena: str = Form(...),
):
    user = login(correo,contrasena)
    return user


@app.post("/subir-libro")
async def subir_documento(
    nombreLibro:str = Form(...),
    contenido: UploadFile=File(...)
):
    try:
        procesarSubida(nombreLibro, contenido)
        
        return {"message": f"Libro {nombreLibro} insertado correctamente ✅"}   

    except Exception as e:
        print(e)
        return {
            "error": "Error al insertar el libro ❌"
        }
    
    

@app.get("/libros")
def obtener_libros():
    try:
        libros = listar_libros()
        return {
            "total": len(libros),
            "libros": libros
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la lista de libros"
        )
@app.delete("/libros/{id_libro}")
def borrar_libro(id_libro: int):
    try:
        eliminado = eliminar_libro(id_libro)

        if not eliminado:
            raise HTTPException(
                status_code=404,
                detail="Libro no encontrado"
            )

        return {
            "message": f"Libro con id {id_libro} eliminado correctamente ✅"
        }

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el libro"
        )




# Ejecutar: uvicorn app:app --reload
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)