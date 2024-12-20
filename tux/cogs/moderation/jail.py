import asyncio

import discord
from discord.ext import commands
from loguru import logger

from prisma.enums import CaseType
from tux.bot import Tux
from tux.utils import checks
from tux.utils.flags import JailFlags, generate_usage

from . import ModerationCogBase


class Jail(ModerationCogBase):
    def __init__(self, bot: Tux) -> None:
        super().__init__(bot)
        self.jail.usage = generate_usage(self.jail, JailFlags)

    @commands.hybrid_command(
        name="jail",
        aliases=["j"],
    )
    @commands.guild_only()
    @checks.has_pl(2)
    async def jail(
        self,
        ctx: commands.Context[Tux],
        member: discord.Member,
        *,
        flags: JailFlags,
    ) -> None:
        """
        Jail a user in the server.

        Parameters
        ----------
        ctx : commands.Context[Tux]
            The discord context object.
        member : discord.Member
            The member to jail.
        flags : JailFlags
            The flags for the command. (reason: str, silent: bool)
        """

        assert ctx.guild

        moderator = ctx.author

        if not await self.check_conditions(ctx, member, moderator, "jail"):
            return

        await ctx.defer(ephemeral=True)

        jail_role_id, jail_channel_id = await asyncio.gather(
            self.config.get_jail_role_id(ctx.guild.id),
            self.config.get_jail_channel_id(ctx.guild.id),
        )

        if jail_role_id is None or (jail_role := ctx.guild.get_role(jail_role_id)) is None:
            await ctx.send("The jail role has not been set up or cannot be found.", ephemeral=True)
            return

        if jail_channel_id is None or ctx.guild.get_channel(jail_channel_id) is None:
            await ctx.send("The jail channel has not been set up or cannot be found.", ephemeral=True)
            return

        if jail_role in member.roles:
            await ctx.send("The user is already jailed.", ephemeral=True)
            return

        user_roles = self._get_manageable_roles(member, jail_role)
        case_user_roles = [role.id for role in user_roles]

        try:
            case = await self.db.case.insert_case(
                guild_id=ctx.guild.id,
                case_user_id=member.id,
                case_moderator_id=ctx.author.id,
                case_type=CaseType.JAIL,
                case_reason=flags.reason,
                case_user_roles=case_user_roles,
            )

            if user_roles:
                await member.remove_roles(*user_roles, reason=flags.reason, atomic=False)

        except Exception as e:
            logger.error(f"Failed to jail {member}. {e}")
            await ctx.send(f"Failed to jail {member}. {e}", ephemeral=True)
            return

        try:
            await member.add_roles(jail_role, reason=flags.reason)
        except (discord.Forbidden, discord.HTTPException) as e:
            logger.error(f"Failed to jail {member}. {e}")
            await ctx.send(f"Failed to jail {member}. {e}", ephemeral=True)
            return

        dm_sent = await self.send_dm(ctx, flags.silent, member, flags.reason, "jailed")
        await self.handle_case_response(ctx, CaseType.JAIL, case.case_number, flags.reason, member, dm_sent)

    @staticmethod
    def _get_manageable_roles(
        member: discord.Member,
        jail_role: discord.Role,
    ) -> list[discord.Role]:
        """
        Get the roles that can be managed by the bot.

        Parameters
        ----------
        member : discord.Member
            The member to jail.
        jail_role : discord.Role
            The jail role.

        Returns
        -------
        list[discord.Role]
            A list of roles that can be managed by the bot.
        """

        return [
            role
            for role in member.roles
            if not (
                role.is_bot_managed()
                or role.is_premium_subscriber()
                or role.is_integration()
                or role.is_default()
                or role == jail_role
            )
            and role.is_assignable()
        ]


async def setup(bot: Tux) -> None:
    await bot.add_cog(Jail(bot))
