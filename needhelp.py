import discord
from discord.ext import commands

TOKEN = "MTI0Nzg4MTI2NDQxODI2MzEyMQ.GIyQxl.aC7h7l55MjrcM4gnId3tzolGm9TZiezxDUUV1o"

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True  # Active les intents pour les états vocaux

bot = commands.Bot(command_prefix='!', intents=intents)


class NeedHelp(commands.Cog):

    # channel_id = -1
    channel_id = 1129427584216743966 # BDA de FlashBack
    temporary_channels = []

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.channel_id == -1:
            return
        channel_name = f"🚨・BDA de {member.display_name}"
        if after.channel and after.channel.id == self.channel_id:  # ID Channel BDA
            temp_channel = await after.channel.clone(name=channel_name)  # Copy
            self.temporary_channels.append(temp_channel.id)
            temp_channel = await temp_channel.edit(user_limit=1)  # Edit

            # Permissions
            await temp_channel.set_permissions(member, connect=True, speak=True, stream=True, view_channel=True)

            await member.move_to(temp_channel)  # Move

        if before.channel and before.channel.id in self.temporary_channels and not before.channel.members:
            await before.channel.delete()


# Admin commands
@bot.tree.command(name="nhconfig", description="Configuration des BDA")
async def slash_command(interaction: discord.Interaction, channel_id: str):
    if interaction.user.guild_permissions.administrator:
        # Verify if the channel exists
        channel = bot.get_channel(int(channel_id))
        if not channel:
            await interaction.response.send_message("Le salon d'attente pour les BDA n'existe pas")
            return

        await interaction.response.send_message("Le salon d'attente pour les BDA est maintenant : <#" + channel_id + ">")
        # Convert string to int
        NeedHelp.channel_id = int(channel_id)
    else:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande")


# Admin commands
@bot.tree.command(name="nhdelete", description="Suppression des BDA")
async def slash_command(interaction: discord.Interaction, category_id: str):
    if interaction.user.guild_permissions.administrator:
        # Delete all voice channel on category id, if name isn't "🚨・Besoin d'aide ?"
        for channel in bot.get_channel(int(category_id)).voice_channels:
            if channel.name != "🚨・Besoin d'aide ?" and not channel.members:
                await channel.delete()
        NeedHelp.temporary_channels.clear()

        await interaction.response.send_message("Toutes les BDA ont été supprimés")
    else:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande")


@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following server:\n')
    for guild in bot.guilds:
        print(f'{guild.name}(id: {guild.id})')
    await bot.tree.sync()  # Add slash commands
    await bot.loop.create_task(setup())  # Add commands


async def setup():
    await bot.wait_until_ready()
    await bot.add_cog(NeedHelp(bot))


bot.run(TOKEN)

# https://discord.com/oauth2/authorize?client_id=1247881264418263121&permissions=285214736&scope=bot
