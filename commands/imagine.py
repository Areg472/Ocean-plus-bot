import discord
from discord import app_commands
from together import Together
import base64
import io

client_together = Together()

async def generate_images(prompt: str):
    response = client_together.images.generate(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-kontext-pro",
        steps=10,
        n=4
    )
    # Return list of base64 images
    return [img.b64_json for img in response.data]

@app_commands.command(name="imagine", description="Generate images from a prompt using AI")
@app_commands.describe(prompt="Describe what you want to see")
async def imagine_command(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    images = await generate_images(prompt)
    files = []
    for idx, b64_img in enumerate(images):
        img_bytes = base64.b64decode(b64_img)
        file = discord.File(io.BytesIO(img_bytes), filename=f"imagine_{idx+1}.png")
        files.append(file)
    await interaction.followup.send(content=f"Images for: `{prompt}`", files=files)

def setup(bot):
    bot.tree.add_command(imagine_command)
