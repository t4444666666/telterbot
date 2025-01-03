import asyncio
import os
import time
from uuid import uuid4

from aiohttp import web  # Add aiohttp for HTTP server
from telethon import TelegramClient, events
from telethon.types import Message, UpdateNewMessage

from terabox import get_data
from tools import (
    get_urls_from_string,
)

bot = TelegramClient("tele", api_id="24704266", api_hash="51c90472a3265056431bd200aa74028e")

# Define /start command to send a welcome message
@bot.on(
    events.NewMessage(
        pattern="/start",
        incoming=True,
        outgoing=False,
    )
)
async def start(m: UpdateNewMessage):
    reply_text = """
◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯
  ✨ TeraBox Video Downloader Bot ✨
◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯◯

Greetings! 🌟 I facilitate seamless downloads from TeraBox.

Simply share the TeraBox link, and I'll retrieve the video for you. 🎬

Supported Formats:
   - .mp4, .mkv, .webm (Max: 500MB)

Ready? Just send the link, and I'll handle the rest. 💬
"""
    await m.reply(
        reply_text,
        link_preview=False,
        parse_mode="markdown",
    )

# Handle incoming messages with TeraBox links
@bot.on(
    events.NewMessage(
        incoming=True,
        outgoing=False,
        func=lambda message: message.text
        and get_urls_from_string(message.text)
        and message.is_private,
    )
)
async def get_message(m: Message):
    url = get_urls_from_string(m.text)
    print(f"Extracted URL: {url}") 
    if not url:
        return await m.reply("Please enter a valid URL.")
    
    data = get_data(url)
    if not data:
        return await m.reply("Sorry! API is dead or maybe your link is broken.")

    if (
        not data["file_name"].endswith(".mp4")
        and not data["file_name"].endswith(".mkv")
        and not data["file_name"].endswith(".webm")
    ):
        return await m.reply(
            "Sorry! File is not supported for now. I can download only .mp4, .mkv, and .webm files."
        )
    
    if int(data["sizebytes"]) > 524288000:
        return await m.reply(
            f"Sorry! File is too big. I can download only 500MB, and this file is {data['size']}."
        )

    start_time = time.time()
    try:
        file = await bot.send_file(
            m.chat.id,
            file=data["direct_link"],
            caption=f"""
File Name: `{data['file_name']}`
Size: **{data['size']}**
Direct Download Link: [Click here]({data['direct_link']})
""",
            supports_streaming=True,
        )
    except Exception as e:
        return await m.reply(
            f"Sorry! Download failed. You can download it from [here]({data['direct_link']}).",
            parse_mode="markdown",
        )

    end_time = time.time()
    total_time = end_time - start_time
    await m.reply(f"Download completed in {total_time:.2f} seconds.")

# Start the bot
async def start_bot():
    await bot.start(bot_token="8053512645:AAEVt7qvltW_LDKULe6L69qwNmY-QvBgG-M")
    await bot.run_until_disconnected()

# Create an HTTP server to bind to a port
async def handle(request):
    return web.Response(text="Telegram Bot is Running.")

def main():
    loop = asyncio.get_event_loop()
    # Set up aiohttp app
    app = web.Application()
    app.router.add_get("/", handle)

    # Run the HTTP server and the bot concurrently
    loop.create_task(start_bot())
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()
