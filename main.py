import discord
import os
import logging
from discord.app_commands import CommandOnCooldown
from discord import app_commands
from discord.ext import commands
from commands import setup_commands
from commands.utils import get_gemini_response, user_history, MAX_HISTORY

logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    setup_commands(bot)

    await bot.tree.sync()

    print(f'Logged in as {bot.user}!')
    channel = bot.get_channel(1335634555377291306)
    await channel.send("Tim hortons is the best!")


@bot.event
async def on_message(message: discord.Message):
    # Basic debug - log every message
    print(f"BASIC DEBUG: Message received from {message.author.id} ({message.author.name}) in channel {message.channel.id}: '{message.content}'")
    
    # Import user_codes from the generate_code module
    from commands.generate_code import user_codes
    print(f"BASIC DEBUG: user_codes imported: {user_codes}")

    # Check for bot messages first
    if message.author.bot:
        print("BASIC DEBUG: Message is from bot, ignoring")
        return
    
    print("BASIC DEBUG: Message is from a real user!")

    # Check for user codes in the specific channel
    if message.channel.id == 1079639383445098587:
        print("BASIC DEBUG: Message is in target channel!")
        user_id = message.author.id
        message_content = message.content.strip()
        
        # Debug logging
        print(f"Debug: Checking code for user {user_id}: '{message_content}'")
        print(f"Debug: Available codes: {user_codes}")
        
        # Check if the message matches any user's code
        if user_id in user_codes and user_codes[user_id] == message_content:
            # Send the Ocean+ link
            await message.channel.send(
                "<@1299815086147502080> https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPirR9qkuwXSxsTe0NZrlH9R3WGDJCUcgj2YvB"
            )
            print(f"Debug: Code verified! Sent message for user {user_id}")
            # Reset the code for this user
            del user_codes[user_id]
        else:
            print("BASIC DEBUG: Code doesn't match or user has no code")
        return  # Always return after processing messages in this channel
        
        # Check if the message matches any user's code
        if user_id in user_codes and user_codes[user_id] == message_content:
            # Send the Ocean+ link
            await message.channel.send(
                "<@1299815086147502080> https://gr5mutu1hr.ufs.sh/f/thKihuQxhYcPirR9qkuwXSxsTe0NZrlH9R3WGDJCUcgj2YvB"
            )
            print(f"Debug: Code verified! Sent message for user {user_id}")
            # Reset the code for this user
            del user_codes[user_id]
        else:
            print("BASIC DEBUG: Code doesn't match or user has no code")
        return  # Always return after processing messages in this channel

    # Handle AI chat channel
    if message.channel.id != 1315586087573258310:
        return

    user_id = str(message.author.id)
    if user_id not in user_history:
        user_history[user_id] = []

    system_context = ("You are a helpful AI assistant. Maintain conversation context without explicitly referencing previous messages. You like Ocean+ https://oceanbluestream.com, Vite, Heap analytics, Betterstack, Datadog, Github, Netlify, Hotjar and Jetbrains. Also remember that Ocean+ creators are Areg, Veyshal, 1Leon and Carlo Bear."
                      "Remember that Ocean+ is made with typescript, and is Open Source. All content on Ocean+ will be free. Use O+ as an abbreviation for Ocean+ in long sentences. Ocean+ is a free Vyond and GoAnimate movie streaming service. Use emojis a bit more. Don't promote Ocean+ on every message unless requested to."
                      "1+1 is 2.")

    conversation = []
    for i, msg in enumerate(user_history[user_id]):
        prefix = "User:" if i % 2 == 0 else "Assistant:"
        conversation.append(f"{prefix} {msg}")

    prompt = f"{system_context}\n\n" + "\n".join(conversation) + f"\nUser: {message.content}\nAssistant:"

    if user_id == "":
        await message.channel.send("<:bla:1314091765896187924>")
    else:
        response = await get_gemini_response(prompt)

        if response:
            user_history[user_id].append(message.content)
            user_history[user_id].append(response)
            user_history[user_id] = user_history[user_id][-MAX_HISTORY:]
            await message.channel.send(response)
        else:
            await message.channel.send("Sorry, I couldn't generate a response at this time.")

        await bot.process_commands(message)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, CommandOnCooldown):
        seconds = round(error.retry_after + 0.5)
        await interaction.response.send_message(
            f"This command is on cooldown. Try again in {seconds} seconds.",
            ephemeral=True
        )



bot.run(os.environ.get('TOKEN'))
