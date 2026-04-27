import json
import os

ARCH_MEMORIA = "memoria_de_ena.json"

def cargar_memoria():
    if os.path.exists(ARCH_MEMORIA):
        try:
            with open(ARCH_MEMORIA, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_memoria(usuario_id, nombre, mensaje_usuario, respuesta_ena):
    memoria = cargar_memoria()
    
    if str(usuario_id) not in memoria:
        memoria[str(usuario_id)] = {
            "nombre": nombre,
            "historial": [],
            "datos_clave": [] # Aquí ENA puede guardar cosas que aprendió (ej. "Le gusta el café")
        }
    
    # Guardamos los últimos 10 intercambios para no saturar el JSON
    historial = memoria[str(usuario_id)]["historial"]
    historial.append({"u": mensaje_usuario, "e": respuesta_ena})
    memoria[str(usuario_id)]["historial"] = historial[-10:]
    
    with open(ARCH_MEMORIA, 'w', encoding='utf-8') as f:
        json.dump(memoria, f, ensure_ascii=False, indent=4)

def obtener_contexto_usuario(usuario_id):
    memoria = cargar_memoria()
    datos = memoria.get(str(usuario_id))
    if datos:
        contexto = f"\n[MEMORIA DE CONVERSACIONES PREVIAS]:\n"
        for h in datos["historial"]:
            contexto += f"Usuario: {h['u']} | ENA: {h['e']}\n"
        return contexto
    return "\n[MEMORIA]: No hay interacciones previas con este usuario."
  
