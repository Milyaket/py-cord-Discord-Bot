import discord, sqlite3
from discord.ext import commands
from discord.commands import slash_command, SlashCommandGroup

# Connect to your sqlite database
your_database = sqlite3.connect("Ticket_System/tickets.db")
your_cursor = your_database.cursor()

# This is a simple ticket bot. Have fun with your new ticket bot. 
# If you have any questions or problems then you can send me a private message on discord - Milyaket#9669
# My projects https://github.com/Milyaket


# If you have team roles then you can add this here.
roles = [] # Example: [123] or if you have more roles [123, 1234, 12345]


class ticket_setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Create a ticket group
    ticket_group = SlashCommandGroup(name="ticket", description="Made by Milyaket#9669")

    @commands.Cog.listener()
    async def on_ready(self):
        # When the bot goes online, it creates a database table if it doesn't exist
        your_cursor.execute("CREATE TABLE IF NOT EXISTS setup(guild INTEGER, channel INTEGER, category INTEGER)")
        your_cursor.execute("CREATE TABLE IF NOT EXISTS user_tickets(guild INTEGER, user INTEGER, ticket_channel INTEGER)")
        self.bot.add_view(view=ticket_view())


    @ticket_group.command(description="Ticket Setup | Made by Milyaket#9669")
    async def setup(self, interaction: discord.Interaction, channel: discord.Option(discord.TextChannel, description="Select the ticket channel | Made by Milyaket#9669"), 
                category: discord.Option(discord.CategoryChannel, description="Select the ticket category | Made by Milyaket#9669")):
        if interaction.user.guild_permissions.administrator:
            # The old ticket setup will be deleted if one exists
            your_cursor.execute("DELETE FROM setup WHERE guild = ?", (interaction.guild.id,))
            your_database.commit()

            # Add this ticket setup
            await add_setup(interaction=interaction, channel=channel, category=category)
        else:
            await interaction.response.send_message(content="You don't have permissions for this command.", ephemeral=True)




def setup(bot):
    bot.add_cog(ticket_setup(bot=bot))




class ticket_view(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open tickets", style=discord.ButtonStyle.gray, custom_id="open_tickets")
    async def open_ticket(self, button: discord.Button, interaction: discord.Interaction):
        await setup_exists(interaction=interaction)





async def add_setup(interaction: discord.Interaction, channel: discord.TextChannel, category: discord.CategoryChannel):
    # All data is now written to the database.
    your_cursor.execute("INSERT INTO setup(guild, channel, category) VALUES(?, ?, ?)", (interaction.guild.id, channel.id, category.id))
    your_database.commit()

    await interaction.response.send_message(content="You have successfully add this setup on your guild.", ephemeral=True)
    # Send the ticket message
    await channel.send(content="Create a ticket \nSource Code: https://github.com/Milyaket", view=ticket_view())



async def setup_exists(interaction: discord.Interaction):
    exists = your_cursor.execute("SELECT * FROM setup WHERE guild = ?", (interaction.guild.id,)).fetchone()
    # If setup exists
    if exists:
        await if_ticket_exists(interaction=interaction)
    else:
        await interaction.response.send_message(content="This setup has been removed by the admin.", ephemeral=True)



async def if_ticket_exists(interaction: discord.Interaction):
    # Here it is checked whether there is already a ticket
    ticket_exists = your_cursor.execute("SELECT ticket_channel FROM user_tickets WHERE guild = ? AND user = ?", (interaction.guild.id, interaction.user.id)).fetchone()

    if ticket_exists:
        for channel in interaction.guild.channels:
            if channel.id == ticket_exists[0]:
                # If a ticket exists, an error message will be sent
                return await interaction.response.send_message(content=f"You have already open a ticket {channel.mention}.", ephemeral=True)
            
        # If no ticket exists, the entry is removed from the database
        your_cursor.execute("DELETE FROM user_tickets WHERE guild = ? AND user = ?", (interaction.guild.id, interaction.user.id))
        your_database.commit()

    # Opens a ticket if one hasn't already been opened.
    await open_a_ticket(interaction=interaction)



async def open_a_ticket(interaction: discord.Interaction):
    ticket_category = your_cursor.execute("SELECT category FROM setup WHERE guild = ?", (interaction.guild.id,)).fetchone()
    category = interaction.guild.get_channel(ticket_category[0])

    # Checks if the category still exists, if not just continue without category.
    if category:
        ticket_channel = await interaction.guild.create_text_channel(name=f"{interaction.user.name}", reason=f"Open a ticket for {interaction.guild.id}", category=category)
    else:
        ticket_channel = await interaction.guild.create_text_channel(name=f"{interaction.user.name}", reason=f"Open a ticket for {interaction.guild.id}")

    await add_permissions(interaction=interaction, ticket_channel=ticket_channel)

    # Ticket data is written to the database
    your_cursor.execute("INSERT INTO user_tickets(guild, user, ticket_channel) VALUES(?, ?, ?)", (interaction.guild.id, interaction.user.id, ticket_channel.id))
    your_database.commit()

    await interaction.response.send_message(content=f"You have successfully open a new ticket {ticket_channel.mention}.", ephemeral=True)
    await ticket_channel.send(content=f"Hello {interaction.user.mention}. \nSource Code: https://github.com/Milyaket")



async def add_permissions(interaction: discord.Interaction, ticket_channel):
    # Set permissions for everyone and for the ticket user
    await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
    await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True, read_messages=True)
    
    # If team roles exist
    if not roles == []:
        for role in roles:
            team_role = interaction.guild.get_role(role)
            # Check if the role exists
            if team_role:
                # Set permissions for the team role
                await ticket_channel.set_permissions(team_role, view_channel=True, send_messages=True, read_messages=True)
