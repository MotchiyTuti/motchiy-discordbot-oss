import tomllib
import os
from .util import send


async def command(message, command=None):
    # 'help' コマンドを処理
    roles = {role.name for role in message.author.roles}
    is_admin = roles & {'admin', 'mod', 'staff'}

    # TOMLファイルからhelpテーブルを読み込む
    toml_path = os.path.join(os.path.dirname(__file__), '../message.toml')
    with open(toml_path, 'rb') as f:
        toml_data = tomllib.load(f)
    help_table = toml_data.get('help', {})

    if command:
        help_text = help_table.get(command, f"No detailed help available for `{command}`.")
    else:
        if is_admin:
            help_text = help_table.get('admin_list', '')
        else:
            help_text = help_table.get('user_list', '')

    await send.message(help_text, message)

async def main(command_args, message):
    if len(command_args) > 1:
        await command(message, command_args[1])
    else:
        await command(message)