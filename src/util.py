from pathlib import Path
from tomlkit import table, dumps, parse #type: ignore
import subprocess
import tomllib
import random
import os
import asyncio
from typing import Any
from typing import cast
import discord  # type: ignore


def execute(command):
    # シェルコマンドを実行
    subprocess.run(command, shell=True, check=True)


def load_system_messages() -> dict[str, Any]:
    try:
        p = Path("message.toml")
        if not p.exists():
            return {}
        with p.open("rb") as f:
            message_toml = tomllib.load(f)
        return message_toml.get("system", {})
    except Exception:
        return {}
    
system_messages = load_system_messages()


def get_permission(member):
    roles_order = ['admin', 'mod', 'staff', 'everyone']
    member_roles = {role.name for role in getattr(member, 'roles', [])}
    for role in roles_order:
        if role in member_roles:
            return role
    return 'everyone'


def hasPermission(member, required_role):
    roles_order = ['everyone', 'staff', 'mod', 'admin']
    member_role = get_permission(member)
    try:
        member_idx = roles_order.index(member_role)
        required_idx = roles_order.index(required_role)
        return member_idx >= required_idx
    except ValueError:
        return False


class send:
    @staticmethod
    async def message(content: str, message: discord.Message) -> None:
        # 先頭に空行を入れる（ゼロ幅スペースで Discord に消されないようにする）
        content = "\u200b\n" + content

        print(content)
        if message is None:
            return

        target = None
        if hasattr(message, "channel"):
            target = message.channel
        elif hasattr(message, "send"):
            target = message
        elif hasattr(message, "response") and hasattr(message.response, "send_message"):
            target = message.response

        if target is None:
            print("No valid target to send message.")
            return

        MAX_LEN = 2000
        try:
            for i in range(0, len(content), MAX_LEN):
                chunk = content[i:i + MAX_LEN]
                await target.send(chunk)
        except Exception as e:
            print(f"Failed to send message: {e}")


def select_option(items):
    options = [x for x in items if x.startswith('--')]
    args = [x for x in items if not x.startswith('--')]
    return options, args


def random_path():
    chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    while True:
        dirname = ''.join(random.choices(chars, k=8))
        full_path = os.path.join('output', dirname)
        if not os.path.exists(full_path):
            return dirname


def create_empty_toml(path: Path):
    empty_data = table()
    with path.open('w', encoding='utf-8') as f:
        f.write(dumps(empty_data))


def load_settings():
    settings_file = Path("settings.toml")
    if not settings_file.exists():
        raise FileNotFoundError("settings.toml not found.")
    with settings_file.open("r", encoding="utf-8") as f:
        return parse(f.read())

settings = load_settings()


async def get_user_input(prompt: str, message: discord.Message) -> str:
    # ユーザーにプロンプトを送信
    await send.message(prompt, message)

    def check(m):
        # メッセージの送信者とチャンネルを確認
        return m.author == message.author and m.channel == message.channel

    try:
        # Bot インスタンスを取得
        bot = message._state._get_client()
        response = await bot.wait_for('message', check=check, timeout=60.0)
        return response.content
    except asyncio.TimeoutError:
        # タイムアウト時のエラーメッセージ
        await send.message("タイムアウトしました。もう一度やり直してください。", message)
        return ""