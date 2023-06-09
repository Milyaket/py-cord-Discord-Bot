import discord, sqlite3, requests, random
from discord.ext import commands
from discord.commands import SlashCommandGroup

# This is a flag-quiz bot. Have fun with your new flag-quiz bot
# If you have any questions or problems then you can send me a private message on discord - Milyaket#9669
# If you want to support me, feel free to do so, just get in touch with me on discord.
# My projects https://github.com/Milyaket

your_database = sqlite3.connect("Flag_Quiz/flag.db")
your_cursor = your_database.cursor()

# Here we get all flags
get_flags = "https://restcountries.com/v3.1/all"

class flag_setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create a flag group
    flag_group = SlashCommandGroup(name="flag-quiz", description="Made by Milyaket#9669")

    @commands.Cog.listener()
    async def on_ready(self):
        your_cursor.execute("CREATE TABLE IF NOT EXISTS setup(guild INTEGER, channel INTEGER, country TEXT, flag_url TEXT)")


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: # Ignore bot messages
            return

        country = your_cursor.execute("SELECT country FROM setup WHERE guild = ?", (message.guild.id,)).fetchone()
        if country: # Checks if there is an entry
            await check_player_input(message=message, country=country)


    @flag_group.command(description="Add the flag quiz setup on your guild | Made by Milyaket#9669")
    async def setup(self, interaction: discord.Interaction, channel: discord.Option(discord.TextChannel, description="Select your channel | Made by Milyaket#9669")):
        if interaction.user.guild_permissions.administrator:
            flag_setup = your_cursor.execute("SELECT * FROM setup WHERE guild = ?", (interaction.guild.id,)).fetchone()
            # Checks if there is not entry yet
            if not flag_setup: # adds the flag quiz
                await add_setup(interaction=interaction, channel=channel)
            else: # removed the flag quiz
                await remove_setup(interaction=interaction)
        else:
            await interaction.response.send_message(content="You don't have permissions for this command.", ephemeral=True)





def setup(bot):
    bot.add_cog(flag_setup(bot=bot))





def get_country():
    # Get random country
    country = random.choice(requests.get(get_flags).json())
    country_name = country['name']['common']
    country_flag_url = country['flags']['png']
    # Returns the country name and country flag
    return country_name, country_flag_url



def quiz_embed(url):
    # Made a quiz embed.
    embed = discord.Embed(description="Which country is that?", color=discord.Color.brand_green())
    embed.set_image(url=url)
    return embed



async def add_setup(interaction: discord.Interaction, channel: discord.TextChannel):
    # Get the country name and the flag
    country_name, country_flag_url = get_country()
    # Adds the setup
    your_cursor.execute("INSERT INTO setup(guild, channel, country, flag_url) VALUES(?, ?, ?, ?)", (interaction.guild.id, channel.id, country_name, country_flag_url))
    your_database.commit()

    await interaction.response.send_message(content="You have successfully add this setup on your guild.", ephemeral=True)
    await channel.send(embed=quiz_embed(url=country_flag_url))



async def remove_setup(interaction: discord.Interaction):
    # Deletes the setup
    your_cursor.execute("DELETE FROM setup WHERE guild = ?", (interaction.guild.id,))
    your_database.commit()

    await interaction.response.send_message(content="I removed the flag quiz setup on this guild. \nIf you want to add this setup, run this command again.", ephemeral=True)



async def check_player_input(message: discord.Message, country):
    if message.content.lower() == country[0].lower():
        # Get new country
        country_name, country_flag_url = get_country()
        # Update the database
        your_cursor.execute("UPDATE setup SET country = ?, flag_url = ? WHERE guild = ?", (country_name, country_flag_url, message.guild.id))
        your_database.commit()
        # Send the new country
        await message.channel.send(content=f"You right {message.author.mention}! Its {country[0]}", embed=quiz_embed(url=country_flag_url))
    else: # If the answer is wrong
        await message.add_reaction("❌")