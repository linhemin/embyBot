from pyrogram import filters

from bot import BotClient
from bot.admin_command import AdminCommandHandler
from bot.event_command import EventHandler
from bot.filters import user_in_group_on_filter, emby_user_on_filter, admin_user_on_filter
from bot.user_command import UserCommandHandler


def setup_command_routes(bot_client: BotClient, user_command_handler: UserCommandHandler,
                         admin_command_handler: AdminCommandHandler, event_handler: EventHandler):
    @bot_client.client.on_message(filters.private & filters.command(["help", "start"]))
    async def c_help(client, message):
        await user_command_handler.help_command(message)

    @bot_client.client.on_message(filters.command("count") & user_in_group_on_filter)
    async def c_count(client, message):
        await user_command_handler.count(message)

    @bot_client.client.on_message(filters.command("info") & user_in_group_on_filter)
    async def c_info(client, message):
        await user_command_handler.info(message)

    @bot_client.client.on_message(filters.private & filters.command("use_code") & user_in_group_on_filter)
    async def c_use_code(client, message):
        await user_command_handler.use_code(message)

    @bot_client.client.on_message(filters.private & filters.command("create") & user_in_group_on_filter)
    async def c_create_user(client, message):
        await user_command_handler.create_user(message)

    @bot_client.client.on_message(
        filters.private & filters.command("reset_emby_password") & user_in_group_on_filter & emby_user_on_filter
    )
    async def c_reset_emby_password(client, message):
        await user_command_handler.reset_emby_password(message)

    @bot_client.client.on_message(
        filters.private & filters.command("select_line") & user_in_group_on_filter & emby_user_on_filter
    )
    async def c_select_line(client, message):
        await user_command_handler.select_line(message)

    @bot_client.client.on_message(filters.command("new_code") & admin_user_on_filter)
    async def c_new_code(client, message):
        await admin_command_handler.new_code(message)

    @bot_client.client.on_message(filters.command("new_whitelist_code") & admin_user_on_filter)
    async def c_new_whitelist_code(client, message):
        await admin_command_handler.new_whitelist_code(message)

    @bot_client.client.on_message(filters.command("ban_emby") & admin_user_on_filter)
    async def c_ban_emby(client, message):
        await admin_command_handler.ban_emby(message)

    @bot_client.client.on_message(filters.command("unban_emby") & admin_user_on_filter)
    async def c_unban_emby(client, message):
        await admin_command_handler.unban_emby(message)

    @bot_client.client.on_message(filters.command("register_until") & admin_user_on_filter)
    async def c_register_until(client, message):
        await admin_command_handler.register_until(message)

    @bot_client.client.on_message(filters.command("register_amount") & admin_user_on_filter)
    async def c_register_amount(client, message):
        await admin_command_handler.register_amount(message)

    @bot_client.client.on_callback_query()
    async def c_select_line_cb(client, callback_query):
        await event_handler.handle_callback_query(client, callback_query)

    @bot_client.client.on_message(filters.left_chat_member | filters.new_chat_members)
    async def group_member_change_handler(client, message):
        await event_handler.group_member_change_handler(client, message)
