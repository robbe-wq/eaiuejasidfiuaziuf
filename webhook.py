import discord
import aiohttp
import io
from discord.ext import commands

# ==================== CONFIGURATION ====================
BOT_TOKEN = "MTU2NDM3OTE5MTEyMDc2MDk0Mg.G6Uki_.WnERGM96zCxXe_Vo84P-HX3z_9L73iItRQ4Hj4"

# The channel ID where the bot listens for original messages
SOURCE_CHANNEL_ID = 1563196523729395736  

# Default fallback webhook URL if the user is not in the 13-user map
DEFAULT_WEBHOOK_URL = "https://discord.com"

# Mapping 13 User IDs to their specific Webhook URLs
USER_WEBHOOK_MAP = {
    1556641425725194261:"https://discord.com/api/webhooks/1564375516109217933/RquvA0GupIglu_HisAD98An4ZlXHHuXAlcUAx1wdoYYbvSpkxBGWciunbjtIPdRDTRno",
    1530657123090960508: "https://discord.com/api/webhooks/1564376810265903224/Pdhss6DulljtKLRn7EGM3AGlw-HKGdO-sttkeaAWaJ8vwFXA_qszQWSOuPcQdaklD5VS",
    1548614512825991270: "https://discord.com/api/webhooks/1564376920924098611/dOS0DF1Xoa_F3NSEVBN9x7jBcjCGeOo2og-soGpld3tT1oV0vyQVsYgigRZlsUT0wzUL",
    1262455175172456512: "https://discord.com/api/webhooks/1564376951429533846/uQVIEytC5_-WWP38MPqFYUo4w-CAZgZgeaFR9HkmEDIOhCSiNGsTRnkDukq4lVbwn3uI",
    1411441793656164493: "https://discord.com/api/webhooks/1564377141804540035/bq1cytJ-yZgfsWNGuqcUB3vVMPp1nA5JiBUk4ynKhYdrSr3QdnE5Oi07rJz1xdxTcvBq",
    955897008210731022: "https://discord.com/api/webhooks/1564377185752453180/7pL5RV56FgdtPvoPtFsa6UzQYw7SkK-u9Zrvw3W-zOuJDu-F6YGVJSd4CcOFLKdEAsRH",
    1561720660525318224: "https://discord.com/api/webhooks/1564377244120514590/g1_8k7IKOEpjtmP-2wk58jvyX_0nRgBUJsP7e0NryQou0chRC94n932nkmb5XNR0PfHf",
    1558409843252002818: "https://discord.com/api/webhooks/1564377342418096279/N7kgfP8sC7llHoCf0iFuY8EFqlBIqW3utVqrxUBcX2tMqXeFUOrEd8VZydGv8hrrNpt_",
    1213530720174215233: "https://discord.com/api/webhooks/1564377537331855611/sAjUpxA3MDKRlnBtEbmvpLu_P_hS2K2_BrVfOa4qlinHQdcY2IV5BVKRtbRK7kbl3Aw1",
    1433831087909634090: "https://discord.com/api/webhooks/1564377823727063231/HXsVd0oOt0iNVsHyJteQ7J8otpaptnFw8_TDAVSPUX8Uq83Z-939ARq9uAbhn86WJLAp",
    1474829162681340054: "https://discord.com/api/webhooks/1564377862465781792/Xjf52GFtnf-YGtKBwJgZCk9rVSsOsVpqeZ0k5JGLJypNPH7uqgBnqY9DXD1suXlyrukS",
    1443014814107566234: "https://discord.com/api/webhooks/1564378118204956756/cfO4sGutF8ENpmQOn0s6ovtr7uUTM7YBDEeZBaSFcef6rCdVBoyAQ0t8YnR2LCEG-i1a",
}

# 3 new unresponsive members map (Add your 3 new user IDs and their target webhooks here)
UNRESPONSIVE_USER_WEBHOOK_MAP = {
    1474829162681340054: "https://discord.com/api/webhooks/1564377862465781792/Xjf52GFtnf-YGtKBwJgZCk9rVSsOsVpqeZ0k5JGLJypNPH7uqgBnqY9DXD1suXlyrukS",
    1213530720174215233: "https://discord.com/api/webhooks/1564377537331855611/sAjUpxA3MDKRlnBtEbmvpLu_P_hS2K2_BrVfOa4qlinHQdcY2IV5BVKRtbRK7kbl3Aw1",
    955897008210731022: "https://discord.com/api/webhooks/1564377185752453180/7pL5RV56FgdtPvoPtFsa6UzQYw7SkK-u9Zrvw3W-zOuJDu-F6YGVJSd4CcOFLKdEAsRH",
}
# =======================================================

intents = discord.Intents.default()
intents.message_content = True  # Required to read text content

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    print("Watching for messages to log...")

@bot.event
async def on_message(message):
    # Ignore messages from bots or other webhooks to prevent loops
    if message.author.bot:
        return

    # Only log messages from your specific source channel
    if message.channel.id != SOURCE_CHANNEL_ID:
        return

    # Check if the author is an unresponsive member or a regular mapped user
    is_unresponsive = message.author.id in UNRESPONSIVE_USER_WEBHOOK_MAP
    
    if is_unresponsive:
        webhook_url = UNRESPONSIVE_USER_WEBHOOK_MAP[message.author.id]
    else:
        webhook_url = USER_WEBHOOK_MAP.get(message.author.id, DEFAULT_WEBHOOK_URL)

    # Format the content text based on whether they are unresponsive or regular
    raw_content = message.content if message.content else ""
    if is_unresponsive:
        content = f"# Unresponsive member has spoken his message is:\n{raw_content}\n"
    else:
        content = raw_content

    # Grab any attachments (images, files, etc.) to forward them too
    files = []
    async with aiohttp.ClientSession() as session:
        for attachment in message.attachments:
            # Re-download the file to pass it to the webhook safely
            file_bytes = await attachment.read()
            # FIX: Changed discord.BytesIO to io.BytesIO
            files.append(discord.File(fp=io.BytesIO(file_bytes), filename=attachment.filename))

        # Setup the webhook connection
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        try:
            # Send text and files while impersonating the user's name/avatar
            await webhook.send(
                content=content,
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url,
                files=files
            )
        except discord.HTTPException as e:
            print(f"Failed to log message from {message.author.name}: {e}")

    await bot.process_commands(message)

bot.run(BOT_TOKEN)
