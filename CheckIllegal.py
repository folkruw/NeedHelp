import discord
from discord.ext import commands
import aiohttp
import json
import logging

TOKEN = ""

bot = commands.Bot(command_prefix='', intents=discord.Intents.default())
MAX_RETRIES = 3
API_URL = "https://logs.flashbackfa.fr/api/Log"
LOG = logging.getLogger('discord')


class CheckIllegal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def get_token():
    # Implement token retrieval logic here
    return "x"


async def get_specific_data(log_types, player_id, search_filter, first_date, last_date):
    data = []
    before_id = 0
    has_more_data = True
    filters = [{"field": "playerId", "operator": "eq", "value": player_id}]

    while has_more_data:
        try:
            print("Calling API...")
            print(log_types, filters, search_filter, first_date, last_date)
            tmp_data = await call_api(log_types, filters, search_filter, before_id)
            print("Data retrieved:", tmp_data)
            if tmp_data is None or not tmp_data:
                break

            for item in tmp_data:
                log_json = item
                created_at = log_json.get("createdAt")
                if first_date <= created_at <= last_date:
                    data.append(log_json)

            if len(tmp_data) == 50 and tmp_data[-1]["createdAt"] >= first_date:
                before_id = tmp_data[-1]["id"]
            else:
                has_more_data = False

        except Exception as e:
            LOG.warning(f"Exception during data retrieval: {e}")
            break

    return data


async def call_api(log_types, filters, search_filter, before_id):
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "logTypes": log_types,
                    "filters": filters,
                    "search": search_filter,
                }
                if before_id > 0:
                    payload["beforeId"] = before_id

                async with session.post(
                        API_URL,
                        headers={
                            "Authorization": "Bearer " + get_token(),
                            "Content-Type": "application/json; utf-8"
                        },
                        json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.text()
                        LOG.info("Successfully called")
                        print("Data retrieved:", data)
                        return json.loads(data)
                    elif response.status == 503:
                        LOG.warning("POST request failed: Service Unavailable (503). Retrying...")
                        attempt += 1
                        if attempt == MAX_RETRIES:
                            LOG.warning("Max retries reached. POST request failed.")
                    elif response.status == 400:
                        LOG.error("POST request failed: Bad Request (400)")
                        break
                    else:
                        LOG.error(f"POST request failed with response code: {response.status}")
                        break
        except Exception as e:
            LOG.error(f"Exception during API call: {e}")
            break

    return None


# Admin commands
@bot.tree.command(name="check", description="Vérification EMS")
async def check_command(interaction: discord.Interaction, unique_id: str):
    if unique_id:
        data = await get_specific_data([38, 53], unique_id, "", "2018-01-01T00:00:00", "2030-01-01T00:00:00")
        # Console log
        print("EMS data retrieved:", data)

        # If no data
        if not data:
            await interaction.response.send_message("Aucune donnée trouvée / Pas d'acte illégal trouvé")
            return
        else:
            json_data = json.dumps(data, indent=4)
            loaded_data = json.loads(json_data)
            messages = [entry['message'] for entry in loaded_data if 'message' in entry]
            await interaction.response.send_message("Acte illégal trouvé" + "\n" + "```" + "\n".join(messages) + "```")


    else:
        await interaction.response.send_message("L'identifiant unique est incorrect")

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following server:\n')
    for guild in bot.guilds:
        print(f'{guild.name}(id: {guild.id})')
    await bot.tree.sync()  # Add slash commands
    await bot.loop.create_task(setup())  # Add commands


async def setup():
    await bot.wait_until_ready()
    await bot.add_cog(CheckIllegal(bot))


bot.run(TOKEN)

# https://discord.com/oauth2/authorize?client_id=1257783410265690233&permissions=285214736&scope=bot

