import discord
from discord.ext import commands

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.create_roles(guild)

    async def create_roles(self, guild):
        existing_roles = [role.name for role in guild.roles]
        required_roles = ['Launcher', 'Viewer']
        for role in required_roles:
            if role not in existing_roles:
                await guild.create_role(name=role)
                print(f"Created {role} role in {guild.name}")

    @commands.command(name="setrole")
    @commands.is_owner()
    async def set_role(self, context, member: discord.Member, role: str):
        """
        Assigns a role to a specified user. This command is restricted to the bot owner.
        :param context: The command context.
        :param member: The member to assign the role to.
        :param role: The role to assign ('Launcher' or 'Viewer').
        """
        role_to_assign = discord.utils.get(context.guild.roles, name=role)
        if role_to_assign:
            await member.add_roles(role_to_assign)
            await context.send(f"Role {role} assigned to {member.display_name}.")
        else:
            await context.send(f"Role {role} not found.")

    @commands.command(name="removerole")
    @commands.is_owner()
    async def remove_role(self, context, member: discord.Member, role: str):
        """
        Removes a role from a specified user. This command is restricted to the bot owner.
        :param context: The command context.
        :param member: The member to remove the role from.
        :param role: The role to remove.
        """
        role_to_remove = discord.utils.get(context.guild.roles, name=role)
        if role_to_remove:
            await member.remove_roles(role_to_remove)
            await context.send(f"Role {role} removed from {member.display_name}.")
        else:
            await context.send(f"Role {role} not found.")

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
