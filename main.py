import discord  # type: ignore
from src import close, open, config, help, status, yt_dlp
from src.util import hasPermission, send, get_permission
from pathlib import Path
import traceback


# Discordクライアント初期化
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    # ボットが準備完了したときに通知
    print(f'Login as {client.user}.')



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
    roles = {role.name for role in message.author.roles}

    # !perm コマンド処理
    if action == 'perm':
        if len(command) < 2:
            # 引数がない場合は送信者自身の権限を表示
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
            if action == 'yt-dlp':
                await yt_dlp.download(command[1:])
                return

        # mod commands
        if hasPermission(message.author, 'mod'):
            if action == 'open':
                await open.main(command, message)
                return
            elif action == 'close':
                await close.main(command, message)
                return

        # admin commands
        if hasPermission(message.author, 'admin'):
            if action == 'dsconf':
                await config.default.main(command, message)
                return

        # 権限不足
        await send.message(str("You do not have permission."), message)

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


if __name__ == "__main__":
    try:
        run_bot()
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        if tb:
            last = tb[-1]
            file_info = f'File \"{last.filename}\", line {last.lineno}'
        else:
            file_info = "No traceback info"
        print('error_occurred', f'Error: {e}\n{file_info}')