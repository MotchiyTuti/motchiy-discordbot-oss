from tomlkit import parse, dumps, table
from pathlib import Path
from .util import send, select_option, create_empty_toml
from typing import List
import re


class default:
    @staticmethod
    async def script(message, subcommand, args):
        servers_file = Path('/mnt/game/default.toml')
        def load_servers():
            if servers_file.exists():
                with servers_file.open('r', encoding='utf-8') as f:
                    return parse(f.read())
            else:
                create_empty_toml(servers_file)
            return table()

        def save_servers(servers):
            with servers_file.open('w', encoding='utf-8') as f:
                f.write(dumps(servers))

        if subcommand == 'ls':
            servers = load_servers()
            if not servers:
                await send.message('No servers found in default.toml', message)
            else:
                server_list = [
                    f"{name} (java={servers[name].get('java_version', 'unknown')})"
                    for name in servers
                ]
                await send.message("Server list:\n" + "\n".join(server_list), message)

        elif subcommand == 'add' and args:
            options, server_names_raw = select_option(args)

            java_version = next((opt.split('=', 1)[1] for opt in options if opt.startswith('--java=')), None)

            servers = load_servers()
            added, already = [], []

            server_names = []
            for raw_name in server_names_raw:
                match = re.match(r'(.+)-(\d+)$', raw_name)
                if match:
                    name, version = match.groups()
                    server_names.append(name)
                    version_from_name = version
                else:
                    name = raw_name
                    server_names.append(name)
                    version_from_name = None

                effective_version = java_version or version_from_name or 'unknown'

                if name in servers:
                    already.append(name)
                else:
                    servers[name] = table()
                    servers[name]["java_version"] = effective_version
                    added.append(name)

            save_servers(servers)

            msg = []
            if added:
                msg.append("Added: " + ", ".join([f'{n} (java={servers[n]["java_version"]})' for n in added]))
            if already:
                msg.append(f'Already in list: {", ".join(already)}')
            await send.message('\n'.join(msg) if msg else 'No servers specified.', message)

        elif subcommand == 'rem' and args:
            options, server_names = select_option(args)
            servers = load_servers()
            removed, notfound = [], []
            for server_name in server_names:
                if server_name in servers:
                    del servers[server_name]
                    removed.append(server_name)
                else:
                    notfound.append(server_name)
            save_servers(servers)
            msg = []
            if removed:
                msg.append(f'Removed: {", ".join(removed)}')
            if notfound:
                msg.append(f'Not in list: {", ".join(notfound)}')
            await send.message('\n'.join(msg) if msg else 'No servers specified.', message)

        else:
            await send.message('Invalid subcommand or arguments for dsconf.', message)


    @staticmethod
    async def main(command: List[str], message):
        if len(command) > 1:
            subcommand = command[1]
            args = command[2:]
            await default.script(message, subcommand, args)
        else:
            await send.message("Invalid command format for 'dsconf'. Usage: dsconf <ls|add|rem> [server_name]", message)
