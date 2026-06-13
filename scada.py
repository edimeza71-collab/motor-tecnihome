import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import CoolProp.CoolProp as CP
import os

# =========================================================
# CONFIGURACIÓN DE LA INTERFAZ
# =========================================================
ctk.set_appearance_mode("Light") 
app = ctk.CTk()
app.geometry("1350x850") 
app.title("Analizador Maestro V5.5 Final - TECNI HOME Blueprint Pro")

scada_frame = ctk.CTkFrame(app, corner_radius=0, border_width=1, border_color="#333")
scada_frame.pack(pady=5, padx=10, fill="both", expand=True)

lienzo = tk.Canvas(scada_frame, bg="#ffffff", highlightthickness=0)
lienzo.pack(fill="both", expand=True)

# Coordenadas Maestras del Plano (ENCOGIDAS para que el dibujo sea más pequeño)
# Coordenadas Maestras (Mismo tamaño compacto, pero DESPLAZADO HACIA ARRIBA)
x_izq, x_der = 365, 965
y_arr, y_aba = 140, 420  # Menos Y significa que todo el bloque sube
x_centro = (x_izq + x_der) / 2
x_centro = (x_izq + x_der) / 2
imagenes_referencia = []

# =========================================================
# FUNCIONES DE DIBUJO (PINZAS Y MANÓMETROS) - INTACTA
# =========================================================
def draw_elitech_clamp(x, y, titulo, color_texto, x_tubo, y_tubo, ruta_img="pinzas.png", unit="°C"):
    lienzo.create_line(x, y, x_tubo, y_tubo, fill="#666", dash=(4,2), width=1)
    lienzo.create_oval(x_tubo-3, y_tubo-3, x_tubo+3, y_tubo+3, fill="#fff", outline="#000", width=1.5)
    
    try:
        img_cruda = Image.open(ruta_img).resize((45, 60))
        img_tk = ImageTk.PhotoImage(img_cruda)
        lienzo.create_image(x, y, image=img_tk, anchor="center")
        imagenes_referencia.append(img_tk)
    except Exception as e:
        lienzo.create_rectangle(x-12, y-20, x+12, y+20, fill="#f2f4f4", outline="#bdc3c7", width=1)
        lienzo.create_text(x, y, text="PINZA", font=("Arial", 7), fill="#7f8c8d")

    lienzo.create_text(x, y + 42, text=titulo, font=("Arial", 7, "bold"), fill=color_texto)
    txt_id = lienzo.create_text(x, y + 53, text=f"-- {unit}", font=("Courier New", 9, "bold"), fill="#111")
    return txt_id

def draw_testo_gauge(x, y, color, x_tubo, y_tubo, ruta_img="testo-550s.png"):
    lienzo.create_line(x, y, x_tubo, y_tubo, fill="#666", dash=(4,2), width=1)
    lienzo.create_oval(x_tubo-4, y_tubo-4, x_tubo+4, y_tubo+4, fill=color, outline="#000", width=1.5)
    
    try:
        img_cruda = Image.open(ruta_img).resize((75, 75))
        img_tk = ImageTk.PhotoImage(img_cruda)
        lienzo.create_image(x, y, image=img_tk, anchor="center")
        imagenes_referencia.append(img_tk) 
    except Exception as e:
        radio = 30
        lienzo.create_oval(x-radio, y-radio, x+radio, y+radio, fill="#f9f9f9", outline=color, width=2)
        lienzo.create_text(x, y, text="IMG", font=("Arial", 6, "bold"), fill="red")
    
    txt_id = lienzo.create_text(x, y + 55, text="-- PSI\n-- °C/°F", font=("Courier New", 9, "bold"), fill="#111", justify="center")
    return txt_id

# Función de ayuda para colocar las imágenes de los equipos
def colocar_imagen_equipo(x, y, ancho, alto, ruta_img, texto_fallback):
    if os.path.exists(ruta_img):
        try:
            img = Image.open(ruta_img).resize((ancho, alto))
            img_tk = ImageTk.PhotoImage(img)
            lienzo.create_image(x, y, image=img_tk, anchor="center")
            imagenes_referencia.append(img_tk)
            return True
        except: pass
    
    # Fallback si no hay imagen
    lienzo.create_rectangle(x-ancho/2, y-alto/2, x+ancho/2, y+alto/2, fill="#f5f5f5", outline="red", width=2)
    lienzo.create_text(x, y, text=f"Error\nImagen\n{texto_fallback}", font=("Arial", 8, "bold"), fill="red", justify="center")
    return False

# =========================================================
# DIBUJO DEL ESQUEMA TÉCNICO - AHORA 100% IMÁGENES
# =========================================================
# Tuberías negras de fondo
# Tuberías negras de fondo (CON ETIQUETAS PARA ANIMARLAS)
lienzo.create_line(x_der, y_aba, x_der, y_arr, fill="#333", width=2.5, tags="tubo_descarga")
lienzo.create_line(x_der, y_arr, x_izq, y_arr, fill="#333", width=2.5, tags="tubo_liquido")
lienzo.create_line(x_izq, y_arr, x_izq, y_aba, fill="#333", width=2.5, tags="tubo_expansion")
lienzo.create_line(x_izq, y_aba, x_der, y_aba, fill="#333", width=2.5, tags="tubo_succion")


# 1. Compresor (Imagen)
colocar_imagen_equipo(x_der, y_aba, 90, 90, "compresor.png", "COMPRESOR")
lienzo.create_text(x_der, y_aba+60, text="COMPRESOR", font=("Arial", 10, "bold"))

# 2. Condensador (REEMPLAZADO: De dibujo a Imagen real)
colocar_imagen_equipo(x_der, y_arr, 130, 90, "condensador.png", "CONDENSADOR")
lienzo.create_text(x_der, y_arr-60, text="CONDENSADOR", font=("Arial", 11, "bold", "underline"), fill="#cc0000")

# 3. Filtro Secador (Imagen)
colocar_imagen_equipo(x_izq + 180, y_arr, 80, 40, "filtro.png", "FILTRO")
lienzo.create_text(x_izq + 180, y_arr-30, text="FILTRO SECADOR", font=("Arial", 8, "bold"))

# 4. VTE (Imagen)
colocar_imagen_equipo(x_izq, y_arr, 60, 60, "vet.png", "VTE")
lienzo.create_text(x_izq, y_arr-40, text="VTE", font=("Arial", 9, "bold"))

# 5. Evaporador (REEMPLAZADO: De dibujo a Imagen real)
colocar_imagen_equipo(x_izq, y_aba, 130, 90, "evaporador.png", "EVAPORADOR")


id_man_baja   = draw_testo_gauge((x_izq + x_der)/2, y_aba + 45, "#0066cc", (x_izq + x_der)/2, y_aba)

# =========================================================
# SECCIÓN DE SENSORES - INTACTA
# =========================================================
id_man_alta   = draw_testo_gauge(x_der - 200, y_arr - 85, "#cc0000", x_der - 200, y_arr)
id_t_out_evap = draw_elitech_clamp(x_izq + 80, y_aba + 100, "SAL. EVAP.", "#0066cc", x_izq + 70, y_aba)
id_t_descarga = draw_elitech_clamp(x_der + 70, y_arr + 80, "ENT. COND.", "#cc0000", x_der, y_arr + 80)
id_t_out_filt = draw_elitech_clamp(x_izq + 80, y_arr - 60, "SAL. FILTRO", "#d35400", x_izq + 80, y_arr)
id_t_out_cond = draw_elitech_clamp(x_der - 120, y_arr - 100, "SAL. COND.", "#cc0000", x_der - 85, y_arr)
id_t_in_comp  = draw_elitech_clamp(x_der - 80, y_aba + 45, "ENT. COMP.", "#0066cc", x_der - 45, y_aba)

id_t_shell    = draw_elitech_clamp(x_der + 120, y_aba + 45, "CARCASA", "#566573", x_der + 20, y_aba)


id_txt_amb_int = draw_elitech_clamp(x_izq - 140, y_aba - 50, "ENTRADA EVAPORADOR", "#0066cc", x_izq, y_aba - 50)
id_txt_diag = lienzo.create_text(x_centro, 300, text="ANALIZADOR MAESTRO TECNI HOME\nESPERANDO INYECCIÓN DE DATOS", font=("Arial", 12, "bold"), justify="center")
id_txt_evap = lienzo.create_text(x_izq, y_aba + 30, text="EVAPORADOR", font=("Arial", 12, "bold"), fill="#0066cc")
# =========================================================
# ANIMACIÓN DEL FLUJO - INTACTA
# =========================================================
part_desc = lienzo.create_oval(0, 0, 8, 8, fill="#ff3333", outline="")
part_liq  = lienzo.create_oval(0, 0, 8, 8, fill="#ffaa00", outline="")
part_exp  = lienzo.create_oval(0, 0, 8, 8, fill="#00ffff", outline="")
part_suc  = lienzo.create_oval(0, 0, 8, 8, fill="#0066cc", outline="")

progreso = 0
def animar_flujo():
    global progreso
    progreso += 1.5
    if progreso > 100: progreso = 0 
    
    y_t1 = y_aba - ((y_aba - y_arr) * (progreso / 100))
    lienzo.coords(part_desc, x_der-4, y_t1-4, x_der+4, y_t1+4)
    x_t2 = x_der - ((x_der - x_izq) * (progreso / 100))
    lienzo.coords(part_liq, x_t2-4, y_arr-4, x_t2+4, y_arr+4)
    y_t3 = y_arr + ((y_aba - y_arr) * (progreso / 100))
    lienzo.coords(part_exp, x_izq-4, y_t3-4, x_izq+4, y_t3+4)
    x_t4 = x_izq + ((x_der - x_izq) * (progreso / 100))
    lienzo.coords(part_suc, x_t4-4, y_aba-4, x_t4+4, y_aba+4)
    
    app.after(45, animar_flujo)

# =========================================================
# PANEL DE CONTROL COMPACTO - INTACTO
# =========================================================
# --- PANEL DE CONTROL ORGANIZADO ---
# Fila 0
# =========================================================
# === INICIO DEL PANEL DE CONTROL (TECNI HOME) ===
# =========================================================

vars_input = {}
ctrl = ctk.CTkFrame(app, fg_color="#eee", border_width=1)
ctrl.pack(pady=5, padx=10, fill="x")
vars_input = {}


# 1. LA FÁBRICA: Le enseñamos a Python cómo armar las cajas
def crear_caja(label, col, row, valor_defecto):
    vars_input[label] = ctk.StringVar(value=valor_defecto)
    ctk.CTkLabel(ctrl, text=label, font=("Arial", 9, "bold")).grid(row=row, column=col*2, padx=2, pady=5, sticky="e")
    ctk.CTkEntry(ctrl, textvariable=vars_input[label], width=55).grid(row=row, column=col*2+1, padx=2, pady=5, sticky="w")

# 2. FILA 0: Presiones y Temperaturas 1
crear_caja("P. Alta (PSI)", 0, 0, "")
crear_caja("P. Baja (PSI)", 1, 0, "")
crear_caja("T. Descarga (°C)", 2, 0, "")
crear_caja("T. Sal. Cond (°C)", 3, 0, "")
crear_caja("T. Ent. Cond (°C)", 4, 0, "")
crear_caja("Tipo Gas", 5, 0, "R22", ["R134a", "R600a", "R22", "R410A", "R32", "R290", "R404A", "R417A"])

# 3. FILA 1: Temperaturas 2
crear_caja("T. Sal. Filt (°C)", 0, 1, "")
crear_caja("T. Sal. Evap (°C)", 1, 1, "")
crear_caja("T. Ent. Comp (°C)", 2, 1, "")
crear_caja("T. Carcasa (°C)", 3, 1, "")
crear_caja("T. Amb. Ext (°C)", 4, 1, "")
crear_caja("T. Amb. Ret (°C)", 5, 1, "")

# 4. LOS GUARDIANES ELÉCTRICOS (Los pongo en la columna 6)
crear_caja("Consumo (A):", 6, 0, "8.5")
crear_caja("RLA Placa (A):", 6, 1, "10.0")

# 5. BOTONES DE ACCIÓN (Alineados a la derecha en la columna 8)


# =========================================================
# === FIN DEL PANEL DE CONTROL ===
# =========================================================
# =========================================================
# LÓGICA DE PROCESAMIENTO - INTACTA
# =========================================================
def procesar():
    try:
        pa, pb = float(vars_input["P. Alta (PSI)"].get()), float(vars_input["P. Baja (PSI)"].get())
        td, toc, tof = float(vars_input["T. Descarga (°C)"].get()), float(vars_input["T. Sal. Cond (°C)"].get()), float(vars_input["T. Sal. Filt (°C)"].get())
        toe, tic, tsh = float(vars_input["T. Sal. Evap (°C)"].get()), float(vars_input["T. Ent. Comp (°C)"].get()), float(vars_input["T. Carcasa (°C)"].get())
        tae, tai = float(vars_input["T. Amb. Ext (°C)"].get()), float(vars_input["T. Amb. Ret (°C)"].get())
        amp = float(vars_input["Consumo (A):"].get())
        gas = vars_input["Tipo Gas"].get()
        p_a_pa = (pa + 14.696) * 6894.76
        p_b_pa = (pb + 14.696) * 6894.76
        tsa = CP.PropsSI('T', 'P', p_a_pa, 'Q', 0, gas) - 273.15
        tsb = CP.PropsSI('T', 'P', p_b_pa, 'Q', 1, gas) - 273.15
        
        tsa_f = (tsa * 9/5) + 32
        tsb_f = (tsb * 9/5) + 32

        sc, sh_u, sh_t = tsa - toc, toe - tsb, tic - tsb
        dt_cond, dt_evap = tsa - tae, tai - tsb
        drop_filtro = toc - tof

        lienzo.itemconfig(id_man_alta, text=f"{pa:.0f} PSI\n{tsa:.1f}°C/{tsa_f:.0f}°F")
        lienzo.itemconfig(id_man_baja, text=f"{pb:.0f} PSI\n{tsb:.1f}°C/{tsb_f:.0f}°F")

        # =========================================================
        # EL SEMÁFORO: ALERTAS VISUALES Y DIAGNÓSTICO
        # =========================================================
        # Mensaje base usando tus variables sc y sh_u
        mensaje_diag = f"SISTEMA ESTABLE\nRecalentamiento (SH): {sh_u:.1f}°C | Subenfriamiento (SC): {sc:.1f}°C"
        color_alerta = "#00ff00" # Verde
        
        # Evaluamos las fallas para cambiar los colores:
        if amp > 15.0: # Ajusta el amperaje de placa aquí
            mensaje_diag = f"¡PELIGRO! SOBRECONSUMO ({amp}A)\nRIESGO EN COMPRESOR"
            color_alerta = "#cc0000" # Rojo
            
        elif sh_u < 2.0:
            mensaje_diag = f"¡ALERTA CRÍTICA! RETORNO DE LÍQUIDO\nSH muy bajo: {sh_u:.1f}°C. Cierra la VTE o saca gas."
            color_alerta = "#00a8e8" # Azul hielo
            
        elif sh_u > 15.0:
            mensaje_diag = f"¡ALERTA! RECALENTAMIENTO ALTO ({sh_u:.1f}°C)\nRevisar posible falta de gas o VTE muy cerrada."
            color_alerta = "orange" # Naranja

        # Mandamos el diagnóstico a la pantalla central
        lienzo.itemconfig(id_txt_diag, text=mensaje_diag, fill=color_alerta)

        # === EL BOMBILLO LED DEL SEMÁFORO ===
        lienzo.delete("luz_semaforo") # Esto borra la luz anterior para que no se amontonen
        # === EL BOMBILLO LED DEL SEMÁFORO (MÁS ARRIBA) ===


        lienzo.delete("luz_semaforo")
        lienzo.create_oval(530, 180, 570, 220, fill=color_alerta, outline="white", width=2, tags="luz_semaforo")
        
        lienzo.itemconfig(id_t_descarga, text=f"{td} °C")
        lienzo.itemconfig(id_t_out_cond, text=f"{toc} °C")
        lienzo.itemconfig(id_t_out_filt, text=f"{tof} °C")
        lienzo.itemconfig(id_t_out_evap, text=f"{toe} °C")
        lienzo.itemconfig(id_t_in_comp, text=f"{tic} °C")
        lienzo.itemconfig(id_t_shell, text=f"{tsh} °C")
        #lienzo.itemconfig(id_txt_amb_ext, text=f"{tae} °C")
        lienzo.itemconfig(id_txt_amb_int, text=f"{tai} °C")

        msg = f"GAS: {gas} | Consumo: {amp}A | SH Útil: {sh_u:.1f}K | SC: {sc:.1f}K\nSH Total: {sh_t:.1f}K | Delta Cond: {dt_cond:.1f}K | Delta Evap: {dt_evap:.1f}K\n"
        diag = "SISTEMA SEGURO - OPERANDO EN PARÁMETROS ÓPTIMOS"
        color = "#009900"


        if drop_filtro > 1.5: diag, color = "ALERTA: RESTRICCIÓN EN FILTRO SECADOR (Caída de T)", "#cc0000"
        elif tsh > 95: diag, color = "PELIGRO: CARCASA SOBRECALENTADA - RIESGO DE ACEITE", "#cc0000"
        elif dt_cond > 17: diag, color = "ALERTA: CONDENSADOR SUCIO O MALA VENTILACIÓN", "#cc6600"

        lienzo.itemconfig(id_txt_diag, text=msg + diag, fill=color)

    except Exception as e:
        lienzo.itemconfig(id_txt_diag, text=f"ERROR: VERIFICA LOS PARÁMETROS O EL TIPO DE GAS\n{str(e)}", fill="red")



# 1. Esta es la función que se activa cuando le das clic al botón
def limpiar_pantalla():
    # 1. Limpiamos todas las variables (StringVar) de presión y temperatura
    for variable in vars_input.values():
        variable.set("")
        
    # 2. Limpiamos la variable del Amperaje
    
    
    # 3. Reseteamos el texto grande del centro
    lienzo.itemconfig(id_txt_diag, text="ANALIZADOR MAESTRO TECNI HOME\nESPERANDO INYECCIÓN DE DATOS", fill="white")

    lienzo.delete("luz_semaforo")
    
    # 4. Mensaje para avisar que todo salió bien
    print("¡Limpieza profunda ejecutada sin errores!")

    # 2. RESETEAR EL TEXTO DEL MEDIO A SU ESTADO ORIGINAL
    lienzo.itemconfig(id_txt_diag, text="ANALIZADOR MAESTRO TECNI HOME\nESPERANDO INYECCIÓN DE DATOS", fill="white")

    # 3. (OPCIONAL) RESETEAR LOS SENSORES A RAYITAS
    # lienzo.itemconfig(id_txt_amb_int, text="RETORNO\n-- °C")
    # Aquí le diremos a Python qué textos o variables borrar
    # Por ahora le ponemos esto para que sepas que funciona
    print("¡Pantalla de datos limpiada!") 
    
    # (Más adelante aquí pondremos los códigos para poner las temperaturas en cero)


# --- BOTONES DE ACCIÓN (NUEVOS Y ALINEADOS A LA DERECHA) ---
btn_procesar = ctk.CTkButton(ctrl, text="PROCESAR", command=procesar, fg_color="#00a8e8", text_color="white", width=100)
btn_procesar.grid(row=0, column=15, padx=(150, 10), pady=5)

btn_limpiar = ctk.CTkButton(ctrl, text="LIMPIAR", command=limpiar_pantalla, fg_color="#cc0000", text_color="white", width=100)
btn_limpiar.grid(row=1, column=15, padx=(150, 10), pady=5)

animar_flujo()
app.mainloop()





animar_flujo()
app.mainloop()

