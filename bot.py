import os
import time
from datetime import timedelta,datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from telegram.constants import ParseMode
from logger import log_this
import asyncio
from urllib.parse import quote

# loading env
load_dotenv()
BOT_TOKEN=os.environ["BOT_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("using start..")
    await update.message.reply_text(text="Hey ! I'm a *URL Encoder* bot.\nJust send me a text, I will give you an URL encoded version of it\nI can also generate a `wa.me` link.\nSend `/help` to see the things i can do.\n\n\n[P](https://t.me/prawmathean) built me *(developer)*.", parse_mode=ParseMode.MARKDOWN)

async def encode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    content = update.message.text
    url_encoded = quote(content)

    await update.message.reply_text(text=f"<pre>{url_encoded}</pre>", parse_mode=ParseMode.HTML)


GET_NUMBER, GET_CONTENT = range(2) # numbers to keep track the user entries on while /wa

async def wa_encode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(text="Okay. Send me a number with country code \n<i>(example: +11231234567)</i>", parse_mode=ParseMode.HTML)

    return GET_NUMBER   # sends user's next message to getnumber 

async def getnumber(update: Update, context: ContextTypes.DEFAULT_TYPE ) -> int:

    number = "".join(filter(str.isdigit, update.message.text))
    
    context.user_data["num"] = number   # saves the number, so that getContent can access the number on next message
    
    await update.message.reply_text(text=f"Got it.\nThe number : <i>{number}</i>\nNow, Send me the content <i>(text to be encoded in the url)</i>", parse_mode=ParseMode.HTML)

    return GET_CONTENT

async def getcontent(update: Update, context: ContextTypes.DEFAULT_TYPE ) -> None:
    content = update.message.text
    num = context.user_data.get("num") # number saved from getnumber

    encoded_url = f"https://wa.me/+{num}/?text={quote(content)}"

    await update.message.reply_text(f"""
    Here's your url :\n\n
    <code> {encoded_url}</code>\n\n
    Generate a <b> Cool QR</b> for this url? Copy paste the URL into [Cool_QR_Bot](https://t.me/cool_QR_Bot)
    """, parse_mode=ParseMode.HTML)

    # clears the context userdata and ends the conversation
    context.user_data.clear()
    return ConversationHandler.END  # end /wa flow

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

async def developer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
    text=(
    "Developed by Prawmathean <i>aka <b>P</b></i>\n\n"
    "<b>Contact</b> : \n"
    '‣ <a href="https://t.me/prawmathean">Telegram</a> \n'
    '‣ <a href="https://prajwal-56.github.io/neobrutal"> Website</a> \n' 
    '‣ <a href="https://github.com/prajwal-56/prawmatheanURLBot_tg"> Github Repo </a>\n'
    ), parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        text="upi : <code>prajwalpraveen2006@okaxis</code>",
        parse_mode=ParseMode.HTML
        )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>_____Help Menu_____</b>\n\n"
        " ‣ <code>/start</code> - To start the bot \n\n"
        " ‣ <code>/help</code> - To view this help menu \n\n"
        " ‣ <code>/wa</code> - To encode a text inside a <a href="">wa.me</a> link. When opened the url, the message is already typed into the chat \n\n"
        " ‣ <code>/developer</code> - To see details about the developer of this bot \n\n"
        " ‣ <code>/support</code> or <code>/donate</code> - To support/donate the developer <i>(UPI)</i> \n\n"
        " ",
        parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


def main(): 
    app = Application.builder().token(BOT_TOKEN).build()

    print(f"This is app : {app}")
    app.add_handler(CommandHandler("start" , start))
    app.add_handler(CommandHandler("help" , help))
    app.add_handler(CommandHandler("developer" , developer))
    app.add_handler(CommandHandler("support" , support))
    app.add_handler(CommandHandler("donate" , support))

    wa_conv = ConversationHandler(
    entry_points=[CommandHandler("wa", wa_encode_handler)],
    states={
        GET_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, getnumber)],
        GET_CONTENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, getcontent)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(wa_conv)

    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, encode ))

    
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()