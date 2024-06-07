import threading
import requests
import json
import inspect
import sys
import os
from flask import Flask
from cryptography.fernet import Fernet
from colorama import Fore, Style, just_fix_windows_console
from discord import app_commands, Intents, Client, Interaction

just_fix_windows_console()

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

def run_flask():
    app.run(host='0.0.0.0', port=8000)

def run_discord_bot():
    # Ensure the user is running Python 3.8 or higher
    if sys.version_info < (3, 8):
        exit("Python 3.8 or higher is required to run this bot!")

    # Check if the discord.py library is installed
    try:
        from discord import app_commands, Intents, Client, Interaction
    except ImportError:
        exit("Either discord.py is not installed or you are running an older and unsupported version of it.")

    # ASCII logo
    logo = f"""
    {Fore.LIGHTBLUE_EX}       {Fore.GREEN}cclloooooooooooooo.
    {Fore.LIGHTBLUE_EX},;;;:{Fore.GREEN}oooooooooooooooooooooo.
    {Fore.LIGHTBLUE_EX};;;;{Fore.GREEN}oooooo{Fore.WHITE}kKXK{Fore.GREEN}ooo{Fore.WHITE}NMMWx{Fore.GREEN}ooooo:..
    {Fore.LIGHTBLUE_EX};;;;{Fore.GREEN}oooooo{Fore.WHITE}XMMN{Fore.GREEN}oooo{Fore.WHITE}XNK0x{Fore.GREEN}dddddoo
    {Fore.LIGHTBLUE_EX};;;;{Fore.GREEN}looo{Fore.WHITE}kNMMWx{Fore.GREEN}ooood{Fore.BLUE}xxxxxxxxxxxxxo
    {Fore.LIGHTBLUE_EX};;;;{Fore.GREEN}ld{Fore.WHITE}kXXXXK{Fore.GREEN}ddddd{Fore.BLUE}xxxxxxxxxxxxxxxx
    {Fore.LIGHTBLUE_EX};;{Fore.BLUE}lxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    {Fore.LIGHTBLUE_EX};;{Fore.BLUE}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    {Fore.LIGHTBLUE_EX};;{Fore.BLUE}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    {Fore.LIGHTBLUE_EX};;{Fore.BLUE}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    {Fore.LIGHTBLUE_EX};;{Fore.BLUE}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    {Fore.LIGHTBLUE_EX};;{Fore.BLUE}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    {Fore.BLUE}ldxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx{Fore.RESET}
    """

    print(logo + inspect.cleandoc(f"""
        Hey, welcome to the active developer badge bot.
        Please enter your bot's token below to continue.

        {Style.DIM}Don't close this application after entering the token
        You may close it after the bot has been invited and the command has been run{Style.RESET_ALL}
    """))

    # Load configuration
    try:
        with open("config.json") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    while True:
        token = os.environ.get("token")
        if token:
            print(f"\n--- Detected token in {Fore.GREEN}./config.json{Fore.RESET} (saved from a previous run). Using stored token. ---\n")
        else:
            token = input("> ")

        try:
            r = requests.get(
                "https://discord.com/api/v10/users/@me",
                headers={"Authorization": f"Bot {token}"}
            )
            data = r.json()
        except requests.exceptions.RequestException as e:
            if e.__class__ == requests.exceptions.ConnectionError:
                exit(f"{Fore.RED}ConnectionError{Fore.RESET}: Discord is commonly blocked on public networks, please make sure discord.com is reachable!")
            elif e.__class__ == requests.exceptions.Timeout:
                exit(f"{Fore.RED}Timeout{Fore.RESET}: Connection to Discord's API has timed out (possibly being rate limited?)")
            exit(f"Unknown error has occurred! Additional info:\n{e}")

        if data.get("id", None):
            break
        print(f"\nSeems like you entered an {Fore.RED}invalid token{Fore.RESET}. Please enter a valid token (see Github repo for help).")
        config.clear()

    with open("config.json", "w") as f:
        config["token"] = token
        json.dump(config, f, indent=2)

    class FunnyBadge(Client):
        def __init__(self, *, intents: Intents):
            super().__init__(intents=intents)
            self.tree = app_commands.CommandTree(self)

        async def setup_hook(self) -> None:
            await self.tree.sync()

    client = FunnyBadge(intents=Intents.none())

    @client.event
    async def on_ready():
        if not client.user:
            raise RuntimeError("on_ready() somehow got called before Client.user was set!")
        print(inspect.cleandoc(f"""
            Logged in as {client.user} (ID: {client.user.id})

            Use this URL to invite {client.user} to your server:
            {Fore.LIGHTBLUE_EX}https://discord.com/api/oauth2/authorize?client_id={client.user.id}&scope=applications.commands%20bot{Fore.RESET}
        """), end="\n\n")

    @client.tree.command()
    async def hello(interaction: Interaction):
        print(f"> {Style.BRIGHT}{interaction.user}{Style.RESET_ALL} used the command.")
        await interaction.response.send_message(inspect.cleandoc(f"""
            Hi **{interaction.user}**, thank you for saying hello to me.

            > __**Where's my badge?**__
            > Eligibility for the badge is checked by Discord in intervals,
            > at this moment in time, 24 hours is the recommended time to wait before trying.

            > __**It's been 24 hours, now how do I get the badge?**__
            > If it's already been 24 hours, you can head to
            > https://discord.com/developers/active-developer and fill out the 'form' there.

            > __**Active Developer Badge Updates**__
            > Updates regarding the Active Developer badge can be found in the
            > Discord Developers server -> https://discord.gg/discord-developers - in the #active-dev-badge channel.
        """))

    client.run(token)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    discord_bot_thread = threading.Thread(target=run_discord_bot)
    discord_bot_thread.start()

    flask_thread.join()
    discord_bot_thread.join()
