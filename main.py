import discord
from src import start, stop, status, help, download, auth, config, present
from src.util import hasPermission, send, get_permission, load_settings
from pathlib import Path
import traceback
import pymysql
import tomllib
import os


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'Login as {client.user}.')
    await main()

@client.event
async def on_message(message):
    # メッセージを処理
    if message.author.bot:
        return

    content = message.content
    if not content.startswith('!'):
        return

    command = content[1:].split()
    if len(command) < 1:
        await send.message(str("Invalid command format."), message)
        return

    action = command[0]

    if action == 'perm':
        if len(command) < 2:
            perm = get_permission(message.author)
            await send.message(str(f"{message.author.display_name} の権限: {perm}"), message)
            return
        name = command[1]
        member = discord.utils.find(lambda m: m.name == name or m.display_name == name, message.guild.members)
        if member is None:
            await send.message(str(f"ユーザー '{name}' が見つかりません。"), message)
            return
        perm = get_permission(member)
        await send.message(str(f"{member.display_name} の権限: {perm}"), message)
        return

    try:
        # everyone commands
        if action in ['status', 'help']:
            if action == 'status':
                await status.main(command, message)
            elif action == 'help':
                await help.main(command, message)
            return

        # staff commands
        if hasPermission(message.author, 'staff'):
            if action == 'dl':
                await download.main(command, message)
                return

        # mod commands
        if hasPermission(message.author, 'mod'):
            if action == 'start':
                await start.main(command, message)
                return
            elif action == 'stop':
                await stop.main(command, message)
                return
            elif action == 'allow':
                await auth.allow(message, *command[1:])
                return
            elif action == 'deny':
                await auth.deny(message, *command[1:])
                return

        # admin commands
        if hasPermission(message.author, 'admin'):
            if action == 'dsconf':
                await config.default.main(command, message)
            if action == 'present':
                await present.main(message)
                return

        await send.message(str("You do not have permission or the command is invalid."), message)

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        if tb:
            last = tb[-1]
            file_info = f'File \"{last.filename}\", line {last.lineno}'
        else:
            file_info = "No traceback info"
        await send.message(str(f'Error: {e}\n{file_info}'), message)
        
def run_bot():
    token_file = Path('token.txt')
    if token_file.exists():
        client.run(token_file.read_text(encoding='utf-8').strip())
    else:
        print('Error: token.txt not found.')


async def main():
    """
    Check if the MySQL connection can be established and send a message.
    """
    settings = load_settings()
    mysql_toml_path = settings['paths']['mysql_toml']
    developer_channel_id = settings['channel_ids']['developer']
    developer_channnel = await client.fetch_channel(developer_channel_id)

    print(f"MySQL configuration path: {mysql_toml_path}")
    if not os.path.exists(mysql_toml_path):
        default_mysql_config = """host = "127.0.0.1"
user = ""
password = ""
database = ""
"""
        with open(mysql_toml_path, "w", encoding="utf-8") as f:
            f.write(default_mysql_config)
        print("mysql.toml が存在しなかったため、デフォルト設定で生成しました。")

    with open(mysql_toml_path, "rb") as f:
        config = tomllib.load(f)

    config_message = "\n".join([
        f"**{key}**: `{value}`" if key != 'password' else "**password**: `****`"
        for key, value in config.items()
    ])
    await send.message(f"**Loaded MySQL Configuration:**\n{config_message}", developer_channnel)

    try:
        connection = pymysql.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            port=config.get("port", 3306)
        )
        connection.close()
        await send.message("MySQLに正常に接続できました。", developer_channnel)
    except Exception as e:
        await send.message(f"MySQL接続エラー: {e}", developer_channnel)

if __name__ == "__main__":
    token_file = Path('token.txt')
    if token_file.exists():
        client.run(token_file.read_text(encoding='utf-8').strip())
    else:
        print('Error: token.txt not found.')