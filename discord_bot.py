import random
import requests
import discord
from discord import app_commands

ESP32_URL = ""  # http://<ip>/data
__TOKEN__ = ""

with open("TOKEN.txt", "r") as f:
    __TOKEN__ = f.readline()

# default profile to prevent errors
current_profile = "Normal Study"

# stores all of the profiles (preset AND custom)
# format: profile[name] = (light_pref, temp_pref, humid_pref, sound_pref)
profiles = {
    "Normal Study": ("BRIGHT", "ROOM", "MID", "MID"),
    "Late Night Study": ("DIM", "COLDER", "LOW", "QUIET"),
    "Exam Cram": ("BRIGHT", "ROOM", "HIGH", "LOUD")
}

# discord client initialization
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Command tree initilization (for slash commands)
tree = app_commands.CommandTree(client)

# client start up function
@client.event
async def on_ready():
    await tree.sync()  # register slash commands globally
    print(f"Logged in as {client.user} (ID: {client.user.id})")

# on any inbound message in a server
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    content = (message.content).lower()

    print(content)

    if ("help me" in content or "steven help" in content) and "hello steven" not in content:
        await message.channel.send("Studying can be stressful. Why don't you take a break and come back to it later? You may also use /help for command help!")


    if ("hello steven" in content or "hi steven" in content or "hey steven" in content or "sup steven" in content) and "help me" not in content:
        await message.channel.send("Hello! Lets get ready to study together!")

    if "joke" in content:

        jokes = [
            "Why do IT professionals hate nature? Because there are too many bugs!",
            "There are 10 types of people who understand binary. Those who do, and those who do not!",
            "How does a Software engineer organize their bath products? Bubblesort!"
        ]

        joke_message = random.choice(jokes)

        await message.channel.send(f"{joke_message} ")



# /test (testing function)
# test bot connection
@tree.command(name="test", description="this is a testing command")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(f"the bot is connected and running.")


# /help (list commands and features)
@tree.command(name="help", description="Learn how to interact with Steven Studyley!")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello! I am Steven Studley, your personal study helper and assistant. All of the current valid commands are: \
 /read, /set_profile, /add_profile, /consult. I am also able to interact in chat with you as well!")


# /read
# read values from HTTP
@tree.command(name="read", description="Read the sensors!")
async def read(interaction: discord.Interaction): 
    response = requests.get(ESP32_URL)
    data = response.json()
    print(data)
    light_value = data["light"]
    temp_value = data["temp"]
    humidity_value = data["humidity"]
    sound_value = data["sound"]
    await interaction.response.send_message(f"Light: {light_value}, Temperature: {temp_value}, Humidity: {humidity_value}, Sound: {sound_value}")
    


# autocomplete for set_profile
# user inputs can only be expected values
async def profile_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=name, value=name)
        for name in profiles.keys()
        if current.lower() in name.lower()
    ]

# /set_profile tree command
@tree.command(name="set_profile", description="Change study profile!")
@app_commands.autocomplete(profile=profile_autocomplete)
async def set_profile(
    interaction: discord.Interaction,
    profile: str    
):
    global current_profile
    current_profile = profile

    await interaction.response.send_message(
        f"Profile switched to **{profile}**!\n"
        f"Values: {profiles[profile]}"
    )

# autocompletes for add_profile
# pref light autocomplete
async def light_autocomplete(interaction, current: str):
    choices = ["BRIGHT", "MID", "DIM"]
    return [
        app_commands.Choice(name=c, value=c)
        for c in choices if current.lower() in c.lower()
    ]

# pref sound autocomplete
async def sound_autocomplete(interaction, current: str):
    choices = ["QUIET", "MID", "LOUD"]
    return [
        app_commands.Choice(name=c, value=c)
        for c in choices if current.lower() in c.lower()
    ]

# pref temp autocomplete
async def temp_autocomplete(interaction, current: str):
    choices = ["COLDER", "ROOM", "WARMER"]
    return [
        app_commands.Choice(name=c, value=c)
        for c in choices if current.lower() in c.lower()
    ]

# pref humid autocomplete
async def humid_autocomplete(interaction, current: str):
    choices = ["LOW", "MID", "HIGH"]
    return [
        app_commands.Choice(name=c, value=c)
        for c in choices if current.lower() in c.lower()
    ]


# /add_profile command
@tree.command(name="add_profile", description="Add a custom study profile!")
@app_commands.autocomplete(
    light_pref=light_autocomplete,
    temp_pref=temp_autocomplete,
    humid_pref=humid_autocomplete,
    sound_pref=sound_autocomplete
)
async def add_profile(
    interaction: discord.Interaction,
    name: str,
    light_pref: str,
    temp_pref: str,
    humid_pref: str,
    sound_pref: str
):
    profiles[name] = (light_pref, temp_pref, humid_pref, sound_pref)

    await interaction.response.send_message(
        f"Added **{name}** with preferences:\n"
        f"Light: {light_pref}, Temp: {temp_pref}, Humid: {humid_pref}, Sound: {sound_pref}"
    )


def check_light(light):
    if light < 180:
        return "DIM"
    if light < 415:
        return "MID"
    if light >= 415:
        return "BRIGHT"

def check_temp(temp):
    if temp < 70:
        return "COLDER"
    if temp < 75:
        return "ROOM"
    if temp >= 75:
        return "WARMER"

def check_humidity(hum):
    if hum < 33:
        return "LOW"
    elif hum < 36:
        return "MID"
    elif hum >= 36:
        return "HIGH"

def check_noise(noise):
    if noise < 1:
        return "QUIET"
    if noise < 1.60:
        return "MID"
    if noise >= 1.60:
        return "LOUD"

def range_checker(light, temp, hum, noise):
    return (check_light(light), check_temp(temp), check_humidity(hum), check_noise(noise))

# /consult
# basically most important function here
@tree.command(name="consult", description="Consult Steven Study for study environment reccomendations!")
async def consult(interaction: discord.Interaction):
    response = requests.get(ESP32_URL)
    data = response.json()
    current_light = data["light"]
    current_temp = data["temp"]
    current_humidity = data["humidity"]
    current_sound = data["sound"]    

    preferred_results = profiles[current_profile]
    current_results = range_checker(current_light, current_temp, current_humidity, current_sound)

    print(preferred_results)
    print(current_results)

    if preferred_results == current_results:
        await interaction.response.send_message(f"Your current study environment meets your preferences! Good luck and get to studying!")


    else:
       
        result_message = "Your current study environment does not meet your preferences. "

        #light value
        if preferred_results[0] != current_results[0]:
            if preferred_results[0] == "DIM":
                result_message += "It is too bright! "
            elif preferred_results[0] == "BRIGHT":
                result_message += "It is too dim! "
            elif preferred_results[0] == "MID" and current_results[0] == "DIM":
                result_message += "It is too dim, you won't be able to see your notes! "
            else:
                result_message += "It is too bright! "
        #temp value
        if preferred_results[1] != current_results[1]:
            if preferred_results[1] == "COLDER":
                result_message += "It is too warm! "
            elif preferred_results[1] == "WARMER":
                result_message += "It is too cold, but a jacket could fix this!  "
            elif preferred_results[1] == "ROOM" and current_results[1] == "COLDER":
                result_message += "It is too cold, but a jacket could fix this!  "
            else:
                result_message += "It is too warm! "
        #humid value
        if preferred_results[2] != current_results[2]:
            if preferred_results[2] == "LOW":
                result_message += "It is too humid! "
            elif preferred_results[2] == "HIGH":
                result_message += "It is too dry, your skin might crack! "
            elif preferred_results[2] == "MID" and current_results[2] == "LOW":
                result_message += "It is too dry, your skin might crack! "
            else:
                result_message += "It is too humid! "
        #sound value
        if preferred_results[3] != current_results[3]:
            if preferred_results[3] == "QUIET":
                result_message += "It is too loud, I recommend wearing noise cancelling headphones! "
            elif preferred_results[3] == "LOUD":
                result_message += "It is way too quiet, your thoughts are too loud! "
            elif preferred_results[3] == "MID" and current_results[3] == "LOW":
                result_message += "It is way too quiet, your thoughts are too loud! "
            else:
                result_message += "It is too loud, I recommend wearing noise cancelling headphones! "

        await interaction.response.send_message(f"{result_message} ")
    


client.run(__TOKEN__)
