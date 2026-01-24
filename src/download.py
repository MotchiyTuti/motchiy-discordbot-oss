import discord
import os
import zipfile
from pathlib import Path
from src.util import send

async def main(command, message):
    if len(command) < 2:
        await send.message("Please specify the message ID.", message)
        return

    message_id = command[1]
    try:
        # Fetch the message using the message ID
        target_message = await message.channel.fetch_message(int(message_id))
    except discord.NotFound:
        await send.message("The specified message could not be found.", message)
        return
    except discord.Forbidden:
        await send.message("You do not have permission to fetch the message.", message)
        return
    except ValueError:
        await send.message("Invalid message ID.", message)
        return

    # Create a directory for saving files
    download_dir = Path("/var/www/html/discord-downloads") / str(message_id)
    download_dir.mkdir(parents=True, exist_ok=True)

    # Save the message content to an md file
    message_file = download_dir / "message.md"
    with message_file.open("w", encoding="utf-8") as f:
        f.write(f"# Message Content\n\n")
        f.write(f"Sender: {target_message.author.display_name}\n")
        f.write(f"Content:\n{target_message.content}\n")

    # Download attachments
    for attachment in target_message.attachments:
        # Save the file with its original name
        original_filename = attachment.filename
        safe_filename = original_filename.encode("utf-8", "ignore").decode("utf-8")
        file_path = download_dir / safe_filename
        await attachment.save(file_path)

    # Create a ZIP file
    zip_path = download_dir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in download_dir.iterdir():
            zipf.write(file, arcname=file.name)

    # Send the download link
    public_url = f"https://motchiy.f5.si/discord-downloads/{message_id}.zip"
    await send.message(f"Download link: {public_url}", message)

    # Delete the temporary directory
    for file in download_dir.iterdir():
        file.unlink()
    download_dir.rmdir()