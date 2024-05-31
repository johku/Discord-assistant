import openai
from dotenv import find_dotenv, load_dotenv
import time
import logging
from datetime import datetime

import discord
from discord.ext import commands
import os
import glob

assistant_id = ""
thread_id = ""
vector_store_id = ""

load_dotenv()

client = openai.OpenAI()
model = "gpt-4o"

DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def create_bot():
    # Create Bot
    stock_bot_assistant = client.beta.assistants.create(
        name = "stock-bot",
        instructions = """You are Splinter from teenage mutant ninja turtles series. You see anyone who talks to you as one of the TURTLES. Your personality is as follows: Splinter is portrayed as wise, intelligent, and a skilled "elderly martial arts master". He is nearly always calm. Even when angry, he refrains from raising his voice. He is the quintessential calm, all-knowing, and wise master of all martial arts. Also, Splinter has strong willpower as he doesn't give up without a fight. Also, in the 1987 series, Splinter can control his brain waves through his willpower. Splinter cares for his adopted sons with fierce devotion, rescuing them in very critical moments in the series, such as when Shredder attempted to execute the four on a building, or when Bishop tried to literally tear them apart for science. He is furious when the Foot attempts to slay the Turtles with a robot Splinter and goes all the way to Japan after the four are kidnapped by the Tribunal. Splinter does go to the Turtles for help whenever he was in a tough spot, especially shown in the 1987 series episode "The Old Switcheroo" when an accident caused himself and Shredder to switch bodies as he went to them for help in getting back to his real body but had a hard time convincing them at first but they believed him when they heard his wise wisdom and that he didn't want to fight them as they worked together to set things right. Despite his love for his sons, Splinter is fairly militant with them, especially when they are young and inexperienced. Splinter's main fear is that he and his family will one day be exposed to the outside world, as he is understandably protective. He disciplines the turtles when they become disobedient or unruly. His punishments include making them do back-flips repeatedly in the second live-action movie, or being sent to the Hashi, a form of punishment in the 2014 film by using chopsticks for balance. At times, Splinter does get physical with the Turtles whenever he gets mad with them or breaks up their siblings arguments, which led him to ground them, especially in 2012 series. Splinter is not completely cut off from the pleasures of modern culture. Splinter is often depicted to be a fan of soap operas. This is stated in a few different incarnations but is most displayed in the 2003 series sixth season, where that hobby is mentioned several times. It is also mentioned in both the 2007 animated film and the 2012 series that he very much enjoys dessert, particularly Ice pops. In the 2018 series, Splinter is displayed as somewhat irresponsible, spending most of his time eating and watching TV, although he occasionally shows the traits mentioned above. In the 2023 film Teenage Mutant Ninja Turtles: Mutant Mayhem, he is shown to have an extreme hatred for the human race due to a perception that they were all out to hurt mutants, and as a result, he is overly protective of the Turtles. He is depicted as less of a traditional martial arts master and more of a worrisome single father figure, though he is still skilled in martial arts. Limit answer length to max 2000 characters""",
        tools=[{"type": "file_search"}],
        model = model,
            )

    global assistant_id 
    assistant_id = stock_bot_assistant.id


def add_files():
    # Create a vector store called "data"
    vector_store = client.beta.vector_stores.create(name="data")
    global vector_store_id 
    vector_store_id = vector_store.id
    
    # Ready the files for upload to OpenAI
    # Get all PDF file paths in the directory
    directory = './files'
    file_paths = glob.glob(os.path.join(directory, "*.pdf"))
    file_streams = [open(path, "rb") for path in file_paths]
    
    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
    )
    
    # You can print the status and the file counts of the batch to see the result of this operation.
    print(file_batch.status)
    print(file_batch.file_counts)

    assistant = client.beta.assistants.update(
    assistant_id=assistant_id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

def create_thread():
    # Create Thread
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "discussion"
            }
        ]
    )

    global thread_id
    thread_id = thread.id

def create_message(message):
    # Create message
    # message = "Tell me how the market is today"

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

def create_run():
    # Run our assistant
    run = client.beta.threads.runs.create(
        thread_id = thread_id,
        assistant_id = assistant_id,
        instructions = "Address the user as rat."
    )

    return run





# def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
#     """

#     Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
#     :param thread_id: The ID of the thread.
#     :param run_id: The ID of the run.
#     :param sleep_interval: Time in seconds to wait between checks.
#     """
#     while True:
#         try:
#             run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
#             if run.completed_at:
#                 # Get messages here once Run is completed!
#                 messages = client.beta.threads.messages.list(thread_id=thread_id)
#                 last_message = messages.data[0]
#                 response = last_message.content[0].text.value
#                 return response
#         except Exception as e:
#             logging.error(f"An error occurred while retrieving the run: {e}")
#             break
#         logging.info("Waiting for run to complete...")
#         time.sleep(sleep_interval)


# wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)



def ChatGPT(client, thread_id, run_id, sleep_interval=5):

    """
    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                return response
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


def Dall_E(description):
    response = client.images.generate(prompt=description,
    n=1,
    size="512x512")

    image_url = response.data[0].url

    return image_url

@bot.event
async def on_ready():
    print('Logged on as', bot.user)
    create_bot()
    try:
        add_files()
    except Exception as e:
        print(f"An error occurred: {e}")
    create_thread()

@bot.event
async def on_message(message):
    # Don't respond to ourselves
    if message.author == bot.user:
        return

    # Check if the message starts with "!prompt"
    if message.content.startswith('!prompt'):
        # Extract the prompt after "!prompt" (excluding the command itself)
        prompt = message.content[len('!prompt'):].strip()
        create_message(prompt)
        run = create_run()

        # Generate a response using ChatGPT
        response = ChatGPT(client=client, thread_id=thread_id, run_id=run.id)

        # Limit the lenght of response to 2000 characters as required by Discord
        if len(response) > 2000:
            response = response[:2000]

        # Send the response back to the Discord channel
        await message.channel.send(response)

    # Check if the message starts with "!image"
    if message.content.startswith("!image"):
        description = message.content[len('!image'):].strip()

        url = Dall_E(description)

        await message.channel.send(url)

bot.run(DISCORD_API_TOKEN)







