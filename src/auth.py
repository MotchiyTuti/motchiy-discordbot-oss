from .util import execute, send

async def modify_whitelist(message, usernames, action):
    try:
        for username in usernames:
            # Perform the whitelist modification
            execute(f'tmux send-keys -t proxy_sv "vwl {action} {username}" ENTER')
            execute(f'tmux send-keys -t proxy_sv "vwl {action} .{username}" ENTER')

        # Notify the user of success
        action_text = "added to" if action == "add" else "removed from"
        await send.message(f'Users {", ".join(usernames)} have been {action_text} the whitelist.', message)
    except Exception as e:
        # Notify the user of any errors
        await send.message(f'An error occurred while processing the whitelist modification: {e}', message)


async def allow(message, *usernames):
    await modify_whitelist(message, usernames, "add")


async def deny(message, *usernames):
    await modify_whitelist(message, usernames, "del")