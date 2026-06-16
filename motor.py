import urllib.request
import csv
import json
import time
import os
import CoolProp.CoolProp as CP
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
# --- LIBRERÍAS PARA INTELIGENCIA ARTIFICIAL ---
from google import genai
import concurrent.futures
import time

# --- CONFIGURACIÓN DE IA (Llave nueva sin VPN) ---
# Pon aquí la clave nuevecita que sacamos hoy en Google AI Studio
import os
# Esto busca la llave en la configuración de Render, no en el archivo
api_key = os.environ.get("GOOGLE_API_KEY") 
cliente_ia = genai.Client(api_key=api_key)

# --- FUNCIÓN DEL INGENIERO IA ---
def consultar_google(instrucciones):
    respuesta = cliente_ia.models.generate_content(
        model='gemini-2.5-flash',
        contents=instrucciones
    )
    return respuesta.text


# =========================================================
# 🛡️ ESCUDO PARA RENDER (SERVIDOR FANTASMA)
# Esto evita que Render apague el programa por falta de puerto
# =========================================================
class ServidorFantasma(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("TECNI HOME PRO: Monitor activo en la nube.".encode('utf-8'))

def arrancar_puerto():
    puerto = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', puerto), ServidorFantasma)
    server.serve_forever()

# Arrancamos el servidor fantasma en segundo plano
threading.Thread(target=arrancar_puerto, daemon=True).start()
# =========================================================

# Configuración URLs y carpeta
ID_HOJA = "1XKKxJkbcTIpSK5t9gLYfKOR7R14AAdNkW-QqeWzGMBE"
URL_LECTURA = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/export?format=csv&gid=0"
URL_LECTURA_ELEC = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/export?format=csv&gid=688032349"
URL_ESCRITURA = "https://script.google.com/macros/s/AKfycbx3lblmeU3FJzU93QW1RQdYE9T-V2YQfOUmBKF9WS76MicT5jioJXPkQumUDWCZXXNL/exec"

os.makedirs("Reportes_TecniHome", exist_ok=True)

print("==================================================")
print(" 🚀 MONITOR EN TIEMPO REAL - TECNI HOME ACTIVADO")
print("==================================================")
print("El servidor de TECNI HOME está vigilando la nube...")

ultima_revision = ""
ultima_revision_elec = ""

def a_num(valor):
    try:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        return float(valor)
    except:
        return 0.0

# --- CEREBRO ELÉCTRICO LOCAL (Cálculo matemático puro) ---
def evaluar_electrico(ocr, ocs, ors, meg, v_entrada, v_salida, cap_placa, v_arr, a_arr):
    alertas = []
    if ocr > 0 and ocs > 0 and ors > 0:
        suma_bobinas = ocr + ocs
        if abs(suma_bobinas - ors) > (ors * 0.10):
            alertas.append("⚠️ BOBINAS: Lecturas anormales (CR+CS ≠ RS). Posible recalentamiento.")
        else:
            alertas.append("✅ BOBINAS: Resistencias en rango.")

    if meg > 0:
        if meg >= 50:
            alertas.append("✅ MEGADO: Aislamiento óptimo (>50 MΩ).")
        elif 20 <= meg < 50:
            alertas.append("⚠️ MEGADO: Aislamiento bajo. Precaución con humedad.")
        else:
            alertas.append("🚨 MEGADO: ¡PELIGRO! Compresor aterrizado (<20 MΩ).")

    if v_entrada > 0 and v_salida > 0:
        v_caida = abs(v_entrada - v_salida)
        if v_caida > 0.5:
            alertas.append(f"🚨 CONTACTOR: Caída de {round(v_caida, 1)}V. Platinos carbonizados.")
        else:
            alertas.append("✅ CONTACTOR: Voltaje pasante óptimo.")

    if cap_placa > 0 and v_arr > 0 and a_arr > 0:
        cap_dinamico = (a_arr * 2652) / v_arr
        diferencia = abs(cap_dinamico - cap_placa)
        tolerancia_maxima = cap_placa * 0.06
        if diferencia > tolerancia_maxima:
            alertas.append(f"🚨 CAPACITOR: Fuera de rango. Placa: {cap_placa}µF | Real: {cap_dinamico:.1f}µF. ¡Reemplazar!")
        else:
            alertas.append(f"✅ CAPACITOR: Óptimo. Trabajando a {cap_dinamico:.1f}µF.")

    if not alertas:
        return "SIN DATOS ELÉCTRICOS"
    return "\n".join(alertas)

while True:
    # ====================================================
    # 🔵 BLOQUE 1: VIGILANCIA TERMODINÁMICA
    # ====================================================
    try:
        respuesta = urllib.request.urlopen(URL_LECTURA)
        lineas = [l.decode('utf-8') for l in respuesta.readlines()]
        lector = list(csv.reader(lineas))
        
        filas_reales = [f for f in lector if len(f) > 5 and f[0].strip() != "" and "Fecha" not in f[0]]
        
        if len(filas_reales) > 0:
            datos = filas_reales[-1]
            
            if datos[0] != ultima_revision:
                ultima_revision = datos[0]
                
                fecha_hora = datos[0]
                cliente = datos[1] if datos[1].strip() != "" else "Cliente Anonimo"
                equipo = datos[2] if len(datos) > 2 else "N/A"
                gas = datos[3] if len(datos) > 3 else "R410A"

                p_alta = a_num(datos[4])
                p_baja = a_num(datos[5])
                t_salida_cond = a_num(datos[7])
                t_salida_evap = a_num(datos[10])
                amp = a_num(datos[15])
                rla = a_num(datos[16])

                print(f"\n🔔 ¡NUEVA REVISIÓN TERMODINÁMICA! Procesando cliente: {cliente.upper()}")

                if t_salida_cond > 130 or t_salida_cond < -30 or p_alta > 500 or p_baja < 0:
                    diag_base = "❌ ERROR: Valores imposibles. Revisa los manómetros."
                    sh = 0.0
                    sc = 0.0
                else:
                    try:
                        p_baja_pa = (p_baja + 14.7) * 6894.76
                        p_alta_pa = (p_alta + 14.7) * 6894.76

                        satura_evap_kelvin = CP.PropsSI('T', 'P', p_baja_pa, 'Q', 1, gas)
                        satura_evap_celsius = satura_evap_kelvin - 273.15
                        sh = t_salida_evap - satura_evap_celsius
                        
                        satura_cond_kelvin = CP.PropsSI('T', 'P', p_alta_pa, 'Q', 0, gas)
                        satura_cond_celsius = satura_cond_kelvin - 273.15
                        sc = satura_cond_celsius - t_salida_cond
                        
                        diag_base = "CALCULADO"
                    except Exception as e:
                        diag_base = f"❌ ERROR DE TABLA: {e}"
                        sh, sc, satura_evap_celsius, satura_cond_celsius = 0.0, 0.0, 0.0, 0.0

                estado_sh = "ÓPTIMO"
                if sh > 12.0: estado_sh = "ALTO (Falta líquido / VET cerrada)"
                elif sh < 4.0: estado_sh = "BAJO (Riesgo de retorno de líquido)"

                estado_sc = "ÓPTIMO"
                if sc > 15.0: estado_sc = "ALTO (Sobrecarga / Condensador sucio)"
                elif sc < 4.0: estado_sc = "BAJO (Falta de gas)"

                if "ERROR" in diag_base: pass 
                elif estado_sh == "ÓPTIMO" and estado_sc == "ÓPTIMO": diag_base = "✅ SISTEMA ESTABLE Y OPERATIVO"
                else: diag_base = "⚠️ REQUIERE ATENCIÓN TÉCNICA (Revisar parámetros)"

                # --- 1. Armamos los datos crudos para que la IA los lea ---
                datos_crudos = (
                    f"Gas: {gas} | Consumo: {amp} A\n"
                    f"Sobrecalentamiento (SH): {sh:.1f}°C ({estado_sh})\n"
                    f"Subenfriamiento (SC): {sc:.1f}°C ({estado_sc})\n"
                    f"Diagnóstico Matemático: {diag_base}"
                )

                # --- 2. Le damos la instrucción al Ingeniero IA ---
                instruccion_ia = f"""
        Actúa como técnico experto en refrigeración industrial y climatización. 
        Analiza el siguiente reporte de campo con datos termodinámicos:
        {datos_crudos}

        Tu informe debe ser una bitácora técnica de uso interno para TECNI HOME, estructurada así:
        1. DIAGNÓSTICO DE FALLA: (Identificación técnica y precisa de la causa raíz de la falla).
        2. ANÁLISIS DE EFICIENCIA: (Interpretación del sobrecalentamiento, subenfriamiento, presiones y consumos).
        3. SOLUCIÓN TÉCNICA DIRECTA: (Pasos exactos de taller a seguir para corregir el problema).
        4. ALERTA DE RIESGO: (Aviso claro si el compresor u otro componente está en peligro inminente según las temperaturas y el RLA).

        IMPORTANTE Y REGLA DE ORO: Si el sistema usa un gas refrigerante del cual no tienes la tabla exacta (como mezclas R417A, sustitutos, etc.), ESTÁ ESTRICTAMENTE PROHIBIDO negarte a dar el diagnóstico. En esos casos, básate en los diferenciales de temperatura (Delta T), los consumos eléctricos y los principios universales de la termodinámica para dar tu veredicto. Usa lenguaje estrictamente de ingeniería de campo, de colega a colega. NO redactes mensajes para el cliente. Sé directo, analítico y sin rodeos.
        """

                # --- 3. Conexión directa a Google ---
                print("🧠 Consultando análisis termodinámico a la IA...")
                try:
                    texto_nube = consultar_google(instruccion_ia)
                    print("✅ El Ingeniero IA respondió correctamente.")
                except Exception as e:
                    print(f"⚠️ Error con la IA: {e}")
                    print("Aplicando Plan B matemático...")
                    # 👇 ESTA ES LA LÍNEA NUEVA QUE VA A MANDAR EL ERROR AL EXCEL 👇
                    texto_nube = f"⚡ FALLA IA: {e} \n\n{datos_crudos}"

                try:
                    payload = {"id": fecha_hora, "cliente": cliente, "diagnostico": texto_nube, "tipo": "termodinamica"}
                    req = urllib.request.Request(URL_ESCRITURA, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                    urllib.request.urlopen(req)
                    print("✅ Resultados termodinámicos inyectados con éxito.")
                    time.sleep(20)
                except Exception as e:
                    print(f"❌ Error al enviar nube: {e}")
    except Exception as e:
        pass

    # ====================================================
    # ⚡ BLOQUE 2: VIGILANCIA ELÉCTRICA
    # ====================================================
    
    try:
        resp_elec = urllib.request.urlopen(URL_LECTURA_ELEC)
        lector_elec = list(csv.reader([l.decode('utf-8') for l in resp_elec.readlines()]))
        filas_elec = [f for f in lector_elec if len(f) > 5 and "ID" not in f[0]]
        
        if len(filas_elec) > 0:
            datos_elec = filas_elec[-1]
            if datos_elec[0] != ultima_revision_elec:
                ultima_revision_elec = datos_elec[0]
                print(f"\n⚡ PROCESANDO ELÉCTRICA ID: {datos_elec[0]}")
                        # === INICIO DEL CEREBRO ELÉCTRICO CON IA ===
                prompt_electrico = f"""
                Eres un técnico especialista en refrigeración. Analiza este diagnóstico eléctrico de campo:
                
                1. CONTACTOR:
                - Caída de tensión medida: {datos_elec[6]} V
                - Si la caída > 2V, marca ALERTA DE DANO.
                
                2. CAPACITOR (Prueba dinámica):
                - V en bornes: {datos_elec[8]} V | Amperaje de arranque: {datos_elec[9]} A
                - C nominal (Placa): {datos_elec[7]} µF
                - REGLA: Calcula la corriente esperada usando la constante 2470: I_esperada = (V * C) / 2470.
                - Compara I_esperada vs Amperaje real para diagnosticar degradación.
                
                3. BOBINADOS y AISLAMIENTO:
                - Medidas: Común-Marcha(CR)={datos_elec[2]}Ω, Común-Arranque(CS)={datos_elec[3]}Ω, Marcha-Arranque(RS)={datos_elec[4]}Ω
                - Megohmios: {datos_elec[5]} MΩ
                - INSTRUCCIÓN: Valida si la suma CR + CS es consistente con RS. Evalúa si el aislamiento es seguro o hay riesgo de irse a tierra.

                Dame un veredicto final: ¿El sistema eléctrico está operativo, requiere mantenimiento o cambio urgente de pieza?
                """
                
                # Le mandamos el mensaje a Gemini y guardamos su respuesta
                print("🧠 Tocando la puerta de Gemini...")
                resultado = consultar_google(prompt_electrico)
                print("✅ Gemini respondió.")
                
                payload_elec = {"id": datos_elec[0], "diagnostico": resultado, "tipo": "electrica"}
                
                print("🚀 Tocando la puerta del Excel...")
                req_e = urllib.request.Request(URL_ESCRITURA, data=json.dumps(payload_elec).encode('utf-8'), headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(req_e, timeout=15) # Le damos 15 segundos máximo
                print("✅ Diagnóstico eléctrico enviado.")
        # === FIN DEL CEREBRO ELÉCTRICO ===

              
    except Exception as e:
        print(f"❌ ERROR ELÉCTRICO: {e}")

    time.sleep(5)