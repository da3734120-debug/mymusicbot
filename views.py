import discord

class QuickButtonView(discord.ui.View):
    def __init__(self, allowed_user, timeout=60.0):
        super().__init__(timeout=timeout)
        self.allowed_user = allowed_user
        self.value = None

    async def handle_click(self, interaction: discord.Interaction, value: str):
        if interaction.user.id != self.allowed_user.id:
            await interaction.response.send_message("❌ You are not allowed to use this button!", ephemeral=True)
            return
        self.value = value
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Accept ✅", style=discord.ButtonStyle.green)
    async def accept_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "accept")

    @discord.ui.button(label="Decline ❌", style=discord.ButtonStyle.red)
    async def decline_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "decline")
