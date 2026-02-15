# Import necessary modules
import tomllib
import pymysql # type: ignore
import asyncio
from datetime import datetime, timedelta
from src.util import get_user_input, send, load_settings

# Load settings from settings.toml
settings = load_settings()

# Load mysql.toml configuration using the path from settings.toml
mysql_toml_path = settings['paths']['mysql_toml']
with open(mysql_toml_path, "rb") as f:
    config = tomllib.load(f)

# Function to update or insert birthday present data into the database
def update_or_insert_birthday_present(connection, name, birthday, amount, request):
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with connection.cursor() as cursor:
        # Check if the name and birthday already exist
        check_sql = """
        SELECT amount, request FROM birthday_presents WHERE name = %s AND birthday = %s
        """
        cursor.execute(check_sql, (name, birthday))
        result = cursor.fetchone()

        if result:
            # Update existing record
            existing_amount, existing_request = result
            new_amount = existing_amount + amount
            new_request = (existing_request or "") + "\n" + (request or "")
            update_sql = """
            UPDATE birthday_presents
            SET amount = %s, request = %s, updated_at = %s
            WHERE name = %s AND birthday = %s
            """
            cursor.execute(update_sql, (new_amount, new_request.strip(), current_date, name, birthday))
        else:
            # Insert new record
            insert_sql = """
            INSERT INTO birthday_presents (name, birthday, amount, request, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (name, birthday, amount, request, current_date))

        connection.commit()
        print("データベースが更新されました。")

# Function to parse space-separated command input
def parse_command_input(content: str) -> dict[str, str]:
    # Parse space-separated command input into a dictionary
    parts = content.split()
    parsed_data = {}

    try:
        parsed_data['name'] = parts[0]
        parsed_data['birthday'] = parts[1]
        parsed_data['amount'] = parts[2]
        parsed_data['request'] = " ".join(parts[3:])
    except IndexError:
        # Raise an error if the input format is incorrect
        raise ValueError("入力形式が正しくありません。名前、誕生日、金額、リクエストの順で入力してください。")

    return parsed_data

# Function to calculate the next birthday
def calculate_next_birthday(birthday: str) -> str:
    # Parse the input birthday string into a datetime object
    birth_date = datetime.strptime(birthday, "%Y-%m-%d")
    today = datetime.now()

    # Set the year of the birthday to the current year
    next_birthday = birth_date.replace(year=today.year)

    # If the birthday this year has already passed, set it to next year
    if next_birthday < today:
        next_birthday = next_birthday.replace(year=today.year + 1)

    return next_birthday.strftime("%Y-%m-%d")

# Function to normalize birthday input into MM-DD format
def normalize_birthday_format(birthday: str) -> str:
    # Replace '/' with '-' for consistency
    birthday = birthday.replace("/", "-")

    # Handle MMDD format
    if len(birthday) == 4 and birthday.isdigit():
        birthday = f"{birthday[:2]}-{birthday[2:]}"

    # Validate the final format
    try:
        datetime.strptime(birthday, "%m-%d")
    except ValueError:
        raise ValueError("誕生日の形式が正しくありません。MM-DD、MM/DD、またはMMDD形式で入力してください。")

    return birthday

# Function to get user input with support for cancel and back commands
async def get_user_input_with_control(prompt: str, message, previous_value=None):
    while True:
        # Send the prompt to the user
        await send.message(f"{prompt}\n(入力を中断するには 'cancel' と入力してください。\n前の選択に戻るには 'back' と入力してください。)", message)

        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            # Wait for user input
            bot = message._state._get_client()
            response = await bot.wait_for('message', check=check, timeout=60.0)
            content = response.content.strip()

            if content.lower() == 'cancel':
                await send.message("操作を中断しました。", message)
                return None, 'cancel'

            if content.lower() == 'back':
                if previous_value is not None:
                    await send.message(f"前の選択に戻ります: {previous_value}", message)
                    return previous_value, 'back'
                else:
                    await send.message("戻る選択肢がありません。", message)
                    continue

            return content, None

        except asyncio.TimeoutError:
            await send.message("タイムアウトしました。もう一度やり直してください。", message)
            return None, 'cancel'

# Function to handle the !present command
async def main(message):
    # Process the !present command
    command_content = message.content.strip()

    if command_content.startswith("!present"):
        # Remove the command part and get the content
        command_args = command_content[len("!present"):].strip()

        if command_args:
            try:
                # Parse space-separated command input
                data = parse_command_input(command_args)
                name = data['name']
                birthday = normalize_birthday_format(data['birthday'])  # Normalize birthday format
                amount = data['amount']
                request = data['request']
            except ValueError as e:
                # Send an error message if parsing fails
                await send.message(f"エラー: {str(e)}", message)
                return
        else:
            # Get input interactively if no arguments are provided
            name = await get_user_input("名前を入力してください：", message)
            if not name:
                return

            birthday = await get_user_input("誕生日を MM-DD、MM/DD、または MMDD 形式で入力してください：", message)
            if not birthday:
                return

            try:
                birthday = normalize_birthday_format(birthday)  # Normalize birthday format
            except ValueError as e:
                await send.message(f"エラー: {str(e)}", message)
                return

            amount = await get_user_input("金額を入力してください：", message)
            if not amount.isdigit():
                await send.message("金額は数字で入力してください。", message)
                return

            request = await get_user_input("リクエスト内容を入力してください：", message)
            if not request:
                return

        # Ensure amount and request are properly initialized
            amount = int(amount) if amount and amount.isdigit() else 0
            request = ""

        # Connect to the database
        connection = pymysql.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            port=config.get("port", 3306)
        )

        try:
            # Update or insert the birthday present data
            update_or_insert_birthday_present(
                connection,
                name=name,
                birthday=birthday,
                amount=int(amount),
                request=request
            )
        finally:
            # Close the database connection
            connection.close()

        # Notify the user on Discord that the database has been updated
        await send.message("データベースが正常に更新されました。", message)
