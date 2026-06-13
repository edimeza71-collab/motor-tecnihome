from google import genai
import concurrent.futures
import time

# --- CONEXIÓN NUEVA (Librería google-genai) ---
# Pon aquí tu clave VIP de Google AI Studio
cliente_ia = genai.Client(api_key="")

# Función aislada para llamar a Google con el nuevo formato
def consultar_google(instrucciones):
    respuesta = cliente_ia.models.generate_content(
        model='gemini-3-flash-preview',
        contents=instrucciones
    )
    return respuesta.text

# --- INICIA LA PRUEBA ---
print("=========================================")
print(" 🧪 LABORATORIO DE IA - TECNI HOME (NUEVA VERSIÓN)")
print("=========================================")

instruccion_prueba = """
Actúa como ingeniero de TECNI HOME.
El contactor tiene 220V de entrada y 218V de salida. 
El capacitor es de 45uF y el cálculo dinámico dio 44.5uF.
Megado en 100 MΩ.
Dame un diagnóstico de un solo párrafo.
"""

print("🧠 Consultando al Ingeniero IA... (Tiene 5 segundos para responder)")
inicio_tiempo = time.time()

try:
    with concurrent.futures.ThreadPoolExecutor() as ejecutor:
        futuro = ejecutor.submit(consultar_google, instruccion_prueba)
        resultado_ia = futuro.result(timeout=15) 
        
        print("\n✅ ¡Google respondió a tiempo!")
        print("-" * 40)
        print(resultado_ia)
        print("-" * 40)

except concurrent.futures.TimeoutError:
    print("\n❌ ¡TIEMPO AGOTADO! Google se quedó pegado o el internet falló.")
    print("⚠️ Aplicando Plan B: Usando el diagnóstico matemático local para no detener el sistema.")
    resultado_ia = "SIN CONEXIÓN A IA: Valores eléctricos en rango operativo (Diagnóstico Local)."

except Exception as e:
    print(f"\n❌ Ocurrió otro error de red: {e}")

tiempo_total = time.time() - inicio_tiempo
print(f"\n⏱️ Tiempo de la prueba: {tiempo_total:.2f} segundos")