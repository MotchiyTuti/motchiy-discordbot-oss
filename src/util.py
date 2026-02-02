from pathlib import Path
from tomlkit import table, dumps, parse #type: ignore
import subprocess
import tomllib
import random
import os
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
        # content をコンソールに出力（デバッグ用）
        print(content)
        if message is None:
            return

        # 出力先を判別：Message オブジェクトなら channel、Channel/その他 send を持つオブジェクトならそれを使う
        target = None
        if hasattr(message, "channel"):
            target = message.channel
        elif hasattr(message, "send"):
            target = message
        # 一部の Interaction 等で response がある場合の対応
        elif hasattr(message, "response") and hasattr(message.response, "send_message"):
            target = message.response

        if target is None:
            # 送信先が見つからなければログだけ出して終了
            print("No valid target to send message.")
            return

        # Discord のメッセージ最大長（約2000文字）に合わせて分割して送信
        MAX_LEN = 2000
        try:
            for i in range(0, len(content), MAX_LEN):
                chunk = content[i:i + MAX_LEN]
                await target.send(chunk)
        except Exception as e:
            # 送信失敗時はログに出す（必要ならここで再試行や詳細ログを追加）
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
    """
    指定されたパスに空のTOMLファイルを作成or上書きする。
    """
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