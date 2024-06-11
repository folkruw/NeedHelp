import discord
from discord.ext import commands

TOKEN = ""

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True  # Active les intents pour les états vocaux

bot = commands.Bot(command_prefix='', intents=intents)


class NeedHelp(commands.Cog):
    # channel_id = -1
    channel_id = [
        1129427584216743966,  # BDA de FlashBack
        1247880599046459420   # Serveur test
    ]
    channel_log_id = -1  # Log
    temporary_channels = []

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not self.channel_id:
            return
        channel_name = f"🚨・BDA de {member.display_name}"
        if after.channel and after.channel.id in self.channel_id:  # ID Channel BDA
            if self.channel_log_id != -1:
                await bot.get_channel(self.channel_log_id).send(f"{member.display_name} a créé une BDA")

            # Copy
            temp_channel = await after.channel.clone(name=channel_name)
            self.temporary_channels.append(temp_channel.id)

            # Edit
            temp_channel = await temp_channel.edit(user_limit=1)

            # Permissions
            await temp_channel.set_permissions(member, connect=True, speak=True, stream=True, view_channel=True)

            # Move
            await member.move_to(temp_channel)

        if before.channel and before.channel.id in self.temporary_channels and not before.channel.members:
            self.temporary_channels.remove(before.channel.id)
            await before.channel.delete()

        ## Join BDA
        if after.channel and after.channel.id in self.temporary_channels:
            if self.channel_log_id != -1:
                await bot.get_channel(self.channel_log_id).send(f"{member.display_name} a rejoint une BDA")


# Admin commands
@bot.tree.command(name="nhc", description="Configuration des BDA")
async def slash_command(interaction: discord.Interaction, channel_id: str):
    if interaction.user.guild_permissions.administrator:
        # If not length 19 and not only number
        if (len(category_id) != 18 and len(category_id) != 19) or not category_id.isdigit():
            await interaction.response.send_message("L'ID de la catégorie est incorrect")
            return

        # Verify if the channel exists
        channel = bot.get_channel(int(channel_id))
        if not channel:
            await interaction.response.send_message("Le salon d'attente pour les BDA n'existe pas")
            return

        await interaction.response.send_message(
            "Le salon d'attente pour les BDA est maintenant : <#" + channel_id + ">")
        # Convert string to int
        NeedHelp.channel_id = int(channel_id)
    else:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande")


@bot.tree.command(name="nhl", description="Logs des BDA")
async def slash_command(interaction: discord.Interaction, channel_id: str):
    if interaction.user.guild_permissions.administrator:
        # Verify if the channel exists
        channel = bot.get_channel(int(channel_id))
        if (len(category_id) != 18 and len(category_id) != 19) or not category_id.isdigit():
            await interaction.response.send_message("L'ID de la catégorie est incorrect")
            return

        await channel.send("Le salon des logs BDA est maintenant : <#" + channel_id + ">")

        # Convert string to int
        NeedHelp.channel_log_id = int(channel_id)
    else:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande")


# Admin commands
@bot.tree.command(name="nhd", description="Suppression des BDA")
async def slash_command(interaction: discord.Interaction, category_id: str):
    if interaction.user.guild_permissions.administrator:
        # If not length 19 and not only number
        if len(category_id) != 19 or not category_id.isdigit():
            await interaction.response.send_message("L'ID de la catégorie est incorrect")
            return

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
