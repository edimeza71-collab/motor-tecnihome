import logging
import io
import asyncio
from PIL import Image
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TimedOut
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# Configurar logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# =========================================================
# 🟢 TUS LLAVES CONFIGURADAS
# =========================================================
TOKEN_TELEGRAM = "8843800483:AAGoPL0wOhD89EBurdoHEg07Paa8-6DUw48"
CLAVE_GEMINI = "AIzaSyAb8RN6LpC6d_ZPN2H6qB--BDCUMPaf84Pdli6Y0oF1mwtGOBvg"

genai.configure(api_key=CLAVE_GEMINI)
modelo_ia = genai.GenerativeModel('gemini-1.5-flash') 

temp_data = {}

def obtener_teclado_estatus():
    return [
        [InlineKeyboardButton("✅ Listo", callback_data='estatus_✅ Listo')],
        [InlineKeyboardButton("✅✅ Pagado", callback_data='estatus_✅✅ Pagado')],
        [InlineKeyboardButton("✳️ En reparación", callback_data='estatus_✳️ En reparación')],
        [InlineKeyboardButton("🅿️ En prueba", callback_data='estatus_🅿️ En prueba')],
        [InlineKeyboardButton("⭕️ Esperando decision", callback_data='estatus_⭕️ Esperando decision')],
        [InlineKeyboardButton("❌ Fuera de servicio", callback_data='estatus_❌ Fuera de servicio')],
        [InlineKeyboardButton("📣 Por pagar", callback_data='estatus_📣 Por pagar')],
        [InlineKeyboardButton("🏠 Domicilio", callback_data='estatus_🏠 Domicilio')]
    ]

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user: return
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    
    temp_data[user_id] = {'foto_id': photo.file_id}
    
    await update.message.reply_text(
        "¡Foto recibida! 📸\n¿En qué estatus está este equipo?", 
        reply_markup=InlineKeyboardMarkup(obtener_teclado_estatus())
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user: return
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data
    
    if user_id not in temp_data: return
    if not data.startswith('estatus_'): return

    estatus_seleccionado = data.replace('estatus_', '')
    foto_id = temp_data[user_id]['foto_id']
    
    await query.edit_message_text(f"Estatus: {estatus_seleccionado} ✅\n\n🤖 *Descargando y leyendo etiqueta...*", parse_mode='Markdown')
    
    try:
        archivo = await context.bot.get_file(foto_id, read_timeout=60)
        image_bytes = await archivo.download_as_bytearray()
        imagen_pil = Image.open(io.BytesIO(image_bytes))
        
        prompt = """
        Lee esta etiqueta de refrigeración. Identifica el tipo de equipo (ej. Nevera, Congelador, Lavadora, Aire Acondicionado), la Marca, el Modelo y el Serial. 
        Devuelve ÚNICAMENTE una sola línea de texto con este formato exacto:
        [Equipo] [Marca] modelo [MODELO] serial [Serial]
        
        OJO: El modelo puede contener letras, o ser EXCLUSIVAMENTE PURO NÚMERO. Si son puros números, extráelo tal cual, no lo ignores.
        
        Ejemplo estricto:
        Nevera LG modelo 145890 serial 123456789
        
        No agregues saludos, ni asteriscos, ni negritas, ni saltos de línea. Solo la línea solicitada.
        """
        
        intentos = 3
        respuesta_ia = None
        
        for i in range(intentos):
            try:
                if i > 0:
                    await query.edit_message_text(f"Estatus: {estatus_seleccionado} ✅\n\n⚠️ La red está pesada. Reintentando lectura (Intento {i+1}/{intentos})...", parse_mode='Markdown')
                
                respuesta_ia = await asyncio.wait_for(
                    asyncio.to_thread(modelo_ia.generate_content, [prompt, imagen_pil]), 
                    timeout=30.0
                )
                break 
                
            except asyncio.TimeoutError:
                if i == intentos - 1:
                    raise 
                await asyncio.sleep(2) 
                
        texto_extraido = respuesta_ia.text.strip()
        mensaje_final = f"{texto_extraido} {estatus_seleccionado}"
        
        # Mandar la foto sola
        await context.bot.send_photo(
            chat_id=user_id, 
            photo=foto_id,
            write_timeout=60,
            read_timeout=60
        )
        
        # Mandar el texto separado para que puedas copiarlo y editarlo facilito
        await context.bot.send_message(
            chat_id=user_id,
            text=mensaje_final
        )
        
        await query.edit_message_text("✅ ¡Listo! ☝️ Ahí tienes tu texto limpio para copiar y editar.")
        
    except asyncio.TimeoutError:
        await query.edit_message_text("❌ La IA no respondió después de 3 intentos. Los servidores andan lentos, intenta de nuevo.")
    except TimedOut:
        await query.edit_message_text("⚠️ El internet parpadeó y Telegram tardó en responder. Vuelve a mandar la foto.")
    except Exception as e:
        await query.edit_message_text(f"❌ Error procesando la foto: {e}")
        
    if user_id in temp_data:
        del temp_data[user_id]

if __name__ == '__main__':
    app = (
        ApplicationBuilder()
        .token(TOKEN_TELEGRAM)
        .connect_timeout(60.0)
        .read_timeout(60.0)
        .write_timeout(60.0)
        .build()
    )
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_button, pattern='^estatus_'))
    print("Bot TECNI HOME listo y volando. ¡A trabajar!")
    app.run_polling()
