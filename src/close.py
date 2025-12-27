from . import status
from .util import execute, system_messages, send
import subprocess


async def server(message, server_name, status, command):
    # 'close' コマンドを処理
    if status == 'waiting':
        await send.message(f'{server_name} is already stopped!', message)
        return
    backend_name = server_name + '_sv'
    close_command = 'end' if '-p' in command else 'stop'

    try:
        # セッションが存在するか先に確認
        check = subprocess.run(f'tmux has-session -t {backend_name}', shell=True, capture_output=True, text=True)
        if check.returncode != 0:
            await send.message(f'No TMUX session named `{backend_name}` found. ({server_name} is not running)', message)
            return

        execute(f'tmux send-keys -t {backend_name} "{close_command}" ENTER')
        execute(f'tmux kill-session -t {backend_name}')
        await send.message(f'{server_name} has been stopped!', message)
    except subprocess.CalledProcessError as e:
        await send.message(f'Failed to stop `{backend_name}`: {e}', message)
    except Exception as e:
        await send.message(f'An unexpected error occurred while closing `{backend_name}`: {e}', message)

async def all(message):
    # 'close all' コマンドを処理
    try:
        result = subprocess.run("tmux list-sessions -F '#S'", shell=True, capture_output=True, text=True)
        sessions = result.stdout.strip().split('\n')
        filtered_sessions = [s for s in sessions if s.endswith('_sv')]

        if not filtered_sessions:
            await send.message('No target TMUX sessions found.', message)
            return

        for session in filtered_sessions:
            execute(f'tmux send-keys -t {session} "stop" ENTER')
            execute(f'tmux send-keys -t {session} "end" ENTER')
            execute(f'tmux kill-session -t {session}')

        await send.message('All target TMUX sessions have been stopped and killed.', message)
    except Exception as e:
        await send.message(f'An error occurred while closing sessions: {e}', message)

async def main(command, message):
    if len(command) > 1 and command[1] == 'all':
        await all(message)
    elif len(command) > 1:
        server_name = command[1]
        backend_name = server_name + '_sv'
        status_val = status.read(backend_name)
        await server(message, server_name, status_val, command)
    else:
        await send.message(system_messages.get("invalid_close", "Invalid command format for 'close'"), message)