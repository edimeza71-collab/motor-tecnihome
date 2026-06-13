import urllib.request
import csv

# Tu ID de la hoja de Tecni Home (intacto)
ID_HOJA = "1XKKxJkbcTIpSK5t9gLYfKOR7R14AAdNkW-QqeWzGMBE"
url = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/export?format=csv"

print("Descargando el último reporte de campo de TECNI HOME...")

try:
    respuesta = urllib.request.urlopen(url)
    lineas = [l.decode('utf-8') for l in respuesta.readlines()]
    lector = list(csv.reader(lineas)) # Convertimos todo en una lista
    
    # Verificamos que haya datos (más de 1 fila, contando los títulos)
    if len(lector) > 1:
        # En Python, el [-1] significa "agarra el último de la lista"
        ultimo_registro = lector[-1] 
        
        print("\n¡Datos capturados con éxito! Aquí está lo que mandaste:\n")
        print(f"➔ Cliente: {ultimo_registro[1]}")
        print(f"➔ Gas: {ultimo_registro[3]}")
        print(f"➔ P. Alta: {ultimo_registro[4]} PSI")
        print(f"➔ P. Baja: {ultimo_registro[5]} PSI")
        print(f"➔ T. Salida Evap: {ultimo_registro[10]} °C")
        print("\n¡El puente entre tu teléfono y el motor Python está 100% operativo!")
        
    else:
        print("\nLa hoja está vacía, mi pana. Solo encontré los títulos.")

except Exception as e:
    print(f"\nVergación, hubo una falla en la lectura: {e}")