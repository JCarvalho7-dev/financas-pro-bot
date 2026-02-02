import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client

# Conexão com Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text # Ex: Almoço 35.50
    try:
        partes = texto.split()
        desc = partes[0]
        valor = float(partes[1].replace(',', '.'))
        
        # Salva no banco de dados que o seu HTML vai ler
        data = {
            "descricao": desc,
            "valor": valor,
            "tipo": "despesa",
            "categoria": "Outros",
            "conta": "Carteira"
        }
        supabase.table("transacoes").insert(data).execute()
        
        await update.message.reply_text(f"✅ Registrado: {desc} R${valor}")
    except:
        await update.message.reply_text("❌ Use o formato: Descrição Valor (Ex: Café 5.00)")

if __name__ == '__main__':
    token = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), registrar))
    app.run_polling()
