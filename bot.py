import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationType

# Configuração de Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Estados do formulário
TIPO, CATEGORIA, VALOR, DESCRICAO = range(4)

# Categorias baseadas no seu Finanças PRO
CATEGORIAS_DESPESA = ['Alimentação', 'Transporte', 'Lazer', 'Moradia', 'Saúde', 'Outros']
CATEGORIAS_RECEITA = ['Salário', 'Investimento', 'Freelance', 'Outros']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['Despesa', 'Receita']]
    await update.message.reply_text(
        "💰 **Finanças PRO Bot**\nEscolha o tipo de transação:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return TIPO

async def escolher_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tipo = update.message.text
    context.user_data['tipo'] = tipo
    
    opcoes = CATEGORIAS_DESPESA if tipo == 'Despesa' else CATEGORIAS_RECEITA
    reply_keyboard = [opcoes[i:i+2] for i in range(0, len(opcoes), 2)] # Divide em linhas de 2
    
    await update.message.reply_text(
        f"Selecione a categoria de {tipo}:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CATEGORIA

async def escolher_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['categoria'] = update.message.text
    await update.message.reply_text("Qual o valor? (Ex: 45.50)", reply_markup=ReplyKeyboardRemove())
    return VALOR

async def registrar_valor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        valor = float(update.message.text.replace(',', '.'))
        context.user_data['valor'] = valor
        await update.message.reply_text("Digite uma breve descrição:")
        return DESCRICAO
    except ValueError:
        await update.message.reply_text("❌ Valor inválido! Digite apenas números.")
        return VALOR

async def finalizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desc = update.message.text
    dados = context.user_data
    
    # Resumo do Lançamento
    resumo = (
        f"✅ **Lançamento Realizado!**\n\n"
        f"🔹 Tipo: {dados['tipo']}\n"
        f"📂 Categoria: {dados['categoria']}\n"
        f"💵 Valor: R$ {dados['valor']:.2f}\n"
        f"📝 Obs: {desc}"
    )
    
    # IMPORTANTE: Aqui você integraria com uma API ou Banco de Dados Futuramente
    await update.message.reply_text(resumo, parse_mode='Markdown')
    return ConversationHandler.END

if __name__ == '__main__':
    # Obtém o token das variáveis de ambiente (Segurança)
    token = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()

    from telegram.ext import ConversationHandler
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TIPO: [MessageHandler(filters.Regex('^(Despesa|Receita)$'), escolher_tipo)],
            CATEGORIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_categoria)],
            VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_valor)],
            DESCRICAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalizar)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    print("Bot rodando...")
    app.run_polling()
