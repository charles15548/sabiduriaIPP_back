from script.controllers.personas import login

from fastapi import FastAPI, HTTPException,Form,File,Body,UploadFile
from fastapi.responses import JSONResponse
from script.controllers.libro import subirLibro
from script.ml.embeddings.subir_libro import extraer_texto
from fastapi.middleware.cors import CORSMiddleware
import uvicorn



from dotenv import load_dotenv
import os
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

@app.post("/acceso")
async def log(
correo: str = Form(...),
contrasena: str = Form(...),
):
    user = login(correo,contrasena)
    return user


@app.post("/subir-libro")
async def subir_documento(
    id_persona: str = Form(...),
    nombreLibro:str = Form(...),
    contenido: UploadFile=File(...)
):
    texto_puro = await extraer_texto(contenido)
    subirLibro(id_persona,nombreLibro,texto_puro)
    return {"message": f"Libro {nombreLibro} insertado correctamente ✅"}   




# Ejecutar: uvicorn app:app --reload
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)