from .util import system_messages, send
import subprocess


def read(server_name):
    # TMUXセッションに同名があれば'running'、なければ'waiting'を返す
    try:
        result = subprocess.run("tmux list-sessions -F '#S'", shell=True, capture_output=True, text=True)
        sessions = result.stdout.strip().split('\n')
        sessions = [s for s in sessions if s]
        filtered_sessions = [s for s in sessions if s.endswith('_sv')]
        if server_name in filtered_sessions:
            return 'running'
        else:
            return 'waiting'
    except Exception:
        return None

def tmux_output(session_name, lines=10):
    # TMUXセッションの最新出力を取得
    try:
        result = subprocess.run(
            f'tmux capture-pane -pt {session_name} -S -{lines}',
            shell=True, capture_output=True, text=True
        )
        return result.stdout
    except Exception:
        return None
    

async def server(message, server_name, status_val):
    # 'status' コマンドを処理
    if status_val:
        await send.message(f'{server_name} is {status_val}', message)
    else:
        await send.message(f'Status file for {server_name} not found.', message)

async def list(message):
    # 'status ls' コマンドを処理
    try:
        result = subprocess.run("tmux list-sessions -F '#S'", shell=True, capture_output=True, text=True)
        sessions = result.stdout.strip().split('\n')
        sessions = [s for s in sessions if s]
        filtered = [s for s in sessions if s.endswith('_sv')]

        # Discord表示用に"_sv"を除去
        display_names = [s[:-3] for s in filtered]

        if display_names:
            await send.message('Currently running servers: ' + ', '.join(display_names), message)
        else:
            await send.message('No servers are currently running.', message)
    except Exception as e:
        await send.message(f'An error occurred while listing tmux sessions: {e}', message)


async def main(command, message):
    if len(command) > 1 and command[1] == 'ls':
        await list(message)
    elif len(command) > 1:
        server_name = command[1]
        backend_name = server_name + '_sv'
        status_val = read(backend_name)
        await server(message, server_name, status_val)
    else:
        await send.message(system_messages.get("invalid_status", "Invalid command format for 'status'"), message)