# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
import uuid

load_dotenv()

app = FastAPI()

#aqui codigo faltante

class EvaluationRequest(BaseModel):
    tema: str
    numero_preguntas: int
    numero_opciones: int
    dificultad: str
    tipo: str

def get_cached_response(key):
    for filename in os.listdir("cache"):
        if filename.endswith(f"{key}.json"):
            with open(f"cache/{filename}", "r") as f:
                return json.load(f)
    return None

def save_to_cache(key, response):
    if not os.path.exists("cache"):
        os.makedirs("cache")
    unique_id = str(uuid.uuid4())
    cache_file = f"cache/{unique_id}_{key}.json"
    with open(cache_file, "w") as f:
        json.dump(response, f)

def generate_prompt(tema, numero_preguntas, numero_opciones, dificultad, tipo):
    prompt = f"""Crea una evaluación sobre el tema "{tema}" con las siguientes características:
    - Número de preguntas: {numero_preguntas}
    - Nivel de dificultad: {dificultad}
    - Tipo de preguntas: {tipo}
    """
    
    if tipo == "mixto":
        prompt += f"""
    - Para preguntas de opción múltiple, usa {numero_opciones} opciones.
    - Mezcla preguntas de opción múltiple y preguntas abiertas.
    """
    elif tipo == "solo opciones":
        prompt += f"""
    - Todas las preguntas deben ser de opción múltiple con {numero_opciones} opciones.
    """
    elif tipo == "solo preguntas libres":
        prompt += """
    - Todas las preguntas deben ser abiertas, para responder textualmente.
    """
    
    prompt += """
    Formato de respuesta:
    {
        "preguntas": [
            {
                "tipo": "opcion_multiple",
                "pregunta": "Texto de la pregunta",
                "opciones": ["Opción A", "Opción B", "Opción C"],
                "respuesta_correcta": "Índice de la opción correcta (0-based)"
            },
            {
                "tipo": "abierta",
                "pregunta": "Texto de la pregunta",
                "respuesta_sugerida": "Una posible respuesta correcta"
            }
        ]
    }
    """
    return prompt

@app.post("/generate_evaluation")
async def generate_evaluation(request: EvaluationRequest):
    cache_key = f"{request.tema}_{request.numero_preguntas}_{request.numero_opciones}_{request.dificultad}_{request.tipo}"
    cached_response = get_cached_response(cache_key)
    if cached_response:
        return {"evaluation": cached_response, "source": "cache"}

    try:
        prompt = generate_prompt(request.tema, request.numero_preguntas, request.numero_opciones, request.dificultad, request.tipo)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente especializado en crear evaluaciones educativas."},
                {"role": "user", "content": prompt}
            ]
        )
        generated_evaluation = json.loads(response.choices[0].message.content)
        save_to_cache(cache_key, generated_evaluation)
        return {"evaluation": generated_evaluation, "source": "openai"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))