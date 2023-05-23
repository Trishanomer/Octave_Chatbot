from pyrogram import Client, filters
from pyrogram.types import *
from pymongo import MongoClient
import requests
import random
import os
import re

API_ID = os.environ.get("18654447", None)
API_HASH = os.environ.get("60ac6f65c766e73dfcc1debef93d06bc", None)
BOT_TOKEN = os.environ.get("5058249365:AAGdFA38VOCppz-IrbmFeCJ4NDGUfXoVbD8", None)
MONGO_URL = os.environ.get("mongodb+srv://abc:abcd@cluster0.r9241sb.mongodb.net/?retryWrites=true&w=majority", None)

bot = Client(
    "VickBot",
    api_id="18654447",
    api_hash="60ac6f65c766e73dfcc1debef93d06bc",
    bot_token="5058249365:AAGdFA38VOCppz-IrbmFeCJ4NDGUfXoVbD8"
)


async def is_admins(chat_id: int):
    return [
        member.user.id
        async for member in bot.iter_chat_members(
            chat_id, filter="administrators"
        )
    ]


@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hi! My name is Ishi. I'm an Artificial Intelligence\n /chatbot - [on|off]")


@bot.on_message(
    filters.command("chatbot off", prefixes=["/", ".", "?", "-"])
    & ~filters.private)
async def chatbotoff(client, message):
    vickdb = MongoClient(MONGO_URL)
    vick = vickdb["VickDb"]["Vick"]
    if message.from_user:
        user = message.from_user.id
        chat_id = message.chat.id
        if user not in (
           await is_admins(chat_id)
        ):
            return await message.reply_text(
                "You are not an admin"
            )
    is_vick = vick.find_one({"chat_id": message.chat.id})
    if not is_vick:
        vick.insert_one({"chat_id": message.chat.id})
        await message.reply_text(f"Chatbot Disabled!")
    if is_vick:
        await message.reply_text(f"ChatBot Is Already Disabled")


@bot.on_message(
    filters.command("chatbot on", prefixes=["/", ".", "?", "-"])
    & ~filters.private)
async def chatboton(client, message):
    vickdb = MongoClient(MONGO_URL)
    vick = vickdb["VickDb"]["Vick"]
    if message.from_user:
        user = message.from_user.id
        chat_id = message.chat.id
        if user not in (
            await is_admins(chat_id)
        ):
            return await message.reply_text(
                "You are not an admin"
            )
    is_vick = vick.find_one({"chat_id": message.chat.id})
    if not is_vick:
        await message.reply_text(f"Chatbot Is Already Enabled")
    if is_vick:
        vick.delete_one({"chat_id": message.chat.id})
        await message.reply_text(f"ChatBot Is Enabled!")


@bot.on_message(
    filters.command("chatbot", prefixes=["/", ".", "?", "-"])
    & ~filters.private)
async def chatbot(client, message):
    await message.reply_text(f"**Usage:**\n/chatbot [on|off] only in a group")


@bot.on_message(
    (filters.text | filters.sticker)
    & ~filters.private
    & ~filters.bot,
)
async def vickai(client: Client, message: Message):
    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    if not message.reply_to_message:
        vickdb = MongoClient(MONGO_URL)
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})
        if not is_vick:
            await bot.send_chat_action(message.chat.id, "typing")
            words = re.findall(r"\w+", message.text.lower())
            random_word = random.choice(words) if words else "hello"
            reply_message = chatai.find_one({"word": random_word})
            if reply_message:
                if random.random() < 0.5:
                    await message.reply_text(reply_message["message"])
                else:
                    await message.reply_sticker(reply_message["message"])
            else:
                await message.reply_text("I don't understand!")
    else:
        if message.reply_to_message.from_user.id == (
            await bot.get_me()
        ).id:
            vickdb = MongoClient(MONGO_URL)
            vick = vickdb["VickDb"]["Vick"]
            is_vick = vick.find_one({"chat_id": message.chat.id})
            if not is_vick:
                await bot.send_chat_action(message.chat.id, "typing")
                words = re.findall(r"\w+", message.text.lower())
                random_word = random.choice(words) if words else "hello"
                reply_message = chatai.find_one({"word": random_word})
                if reply_message:
                    if random.random() < 0.5:
                        await message.reply_text(reply_message["message"])
                    else:
                        await message.reply_sticker(reply_message["message"])
                else:
                    await message.reply_text("I don't understand!")


@bot.on_message(
    (filters.sticker | filters.text)
    & filters.private
    & ~filters.bot,
)
async def vickprivate(client: Client, message: Message):
    vickdb = MongoClient(MONGO_URL)
    vick = vickdb["VickDb"]["Vick"]
    is_vick = vick.find_one({"chat_id": message.chat.id})
    if not is_vick:
        await bot.send_chat_action(message.chat.id, "typing")
        words = re.findall(r"\w+", message.text.lower())
        random_word = random.choice(words) if words else "hello"
        reply_message = chatai.find_one({"word": random_word})
        if reply_message:
            if random.random() < 0.5:
                await message.reply_text(reply_message["message"])
            else:
                await message.reply_sticker(reply_message["message"])
        else:
            await message.reply_text("I don't understand!")


@bot.on_message(
    (filters.sticker | filters.text)
    & filters.private
    & ~filters.bot,
)
async def vickprivatesticker(client: Client, message: Message):
    vickdb = MongoClient(MONGO_URL)
    vick = vickdb["VickDb"]["Vick"]
    is_vick = vick.find_one({"chat_id": message.chat.id})
    if not is_vick:
        await bot.send_chat_action(message.chat.id, "typing")
        words = re.findall(r"\w+", message.text.lower())
        random_word = random.choice(words) if words else "hello"
        reply_message = chatai.find_one({"word": random_word})
        if reply_message:
            if random.random() < 0.5:
                await message.reply_text(reply_message["message"])
            else:
                await message.reply_sticker(reply_message["message"])
        else:
            await message.reply_text("I don't understand!")


bot.run()
