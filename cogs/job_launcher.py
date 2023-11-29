"""
Author Sarthak Vijayvergiya - https://github.com/sarthakvijayvergiya
Description: A Discord bot that helps in launching jobs, setting API keys, and configuring result channels for the Human Protocol.
"""

from discord.ext import commands
from discord.ext.commands import Context
import asyncio
from discord.ext import tasks
from datetime import datetime, timedelta
import os
import json
from services.external_api_handler import ExternalAPIHandler


class JobLauncher(commands.Cog, name="JobLauncher"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.job_queue = []  # A list to keep track of jobs to publish results for
        self.external_api_handler = ExternalAPIHandler()
        self.result_check_interval = int(
            os.getenv("RESULT_CHECK_INTERVAL", 180)
        )  # Default to 180 seconds


    def cog_unload(self):
        self.publish_results.cancel()  # Cancel the background task when the cog is unloaded
        self.external_api_handler.close_session()

    @tasks.loop(
        seconds=60
    )  # Temporary interval, will be reset in before_publish_results
    async def publish_results(self):
        for job in self.job_queue:
            results = await self.external_api_handler.check_job_result(
                job["api_key"], job["job_id"]
            )
            if results:
                # Assuming that the job is considered complete if any results are returned
                result_channel = self.bot.get_channel(job["result_channel_id"])
                if result_channel:
                    for result in results:
                        message = f"Job ID: {job['job_id']}, Worker Address: {result['workerAddress']}, Solution: {result['solution']}"
                        if 'error' in result and result['error']:
                            message += f", Error: {result['error']}"
                        await result_channel.send(message)
                    self.job_queue.remove(
                        job
                    )  # Remove job from queue after publishing results

    @publish_results.before_loop
    async def before_publish_results(self):
        await self.bot.wait_until_ready()  # Wait until the bot is ready before starting the loop
        self.publish_results.change_interval(
            seconds=self.result_check_interval
        )  # Set the actual interval

    @commands.command(name="setAPIKey")
    async def set_api_key_command(self, context: Context):
        api_key = await self.ask(context, "Please provide your API key secret")
        if api_key is None:
            return

        await self.bot.database.add_api_key(context.author.id, api_key)

        await context.send("API key set successfully.")

    @commands.command(name="setResultChannel")
    async def set_result_channel_command(self, context: Context, channel_id: int):
        await self.bot.database.add_result_channel(context.author.id, channel_id)
        await context.send("Result channel set successfully.")

    @commands.command(name="launchJob")
    async def launch_job(self, context: Context):
        settings = await self.bot.database.get_user_settings(context.author.id)

        # Check if both API key and result channel have been set
        if not settings or not settings[0] or not settings[1]:
            missing_settings = []
            if not settings or not settings[0]:
                missing_settings.append("API key")
            if not settings or not settings[1]:
                missing_settings.append("result channel")
            await context.send(
                f"You need to set the following before launching a job: {', '.join(missing_settings)}. "
                f"Use the commands `!setAPIKey` and `!setResultChannel <CHANNEL_ID>`."
            )
            return

        api_key = settings[0]
        result_channel_id = settings[1]

        await context.send(
            "Let's launch a new job. I will need some information from you."
        )

        requesterTitle = await self.ask(context, "What is the title for the job?")
        if requesterTitle is None:
            return

        submissionsRequired = await self.ask(
            context, "How many submissions are required?"
        )
        if submissionsRequired is None:
            return

        requesterDescription = await self.ask(
            context, "Please provide a description for the requester."
        )
        if requesterDescription is None:
            return

        fundAmount = await self.ask(context, "What is the fund amount for this job?")
        if fundAmount is None:
            return

        # Step to select the network
        supported_networks_str = os.getenv("SUPPORTED_NETWORKS")
        supported_networks = json.loads(supported_networks_str.replace("'", '"'))
        network_choice = await self.ask(
            context, f"Select a network: {', '.join(supported_networks.keys())}"
        )
        if network_choice is None or network_choice not in supported_networks:
            await context.send("Invalid network selection. Job launch cancelled.")
            return
        network_chain_id = supported_networks[network_choice]

        # Confirm the details with the user before proceeding
        await context.send(
            f"Please confirm the details:\n"
            f"Title: {requesterTitle}\n"
            f"Submissions Required: {submissionsRequired}\n"
            f"Description: {requesterDescription}\n"
            f"Fund Amount: {fundAmount}\n"
            f"Netowrk: {network_choice}\n"
            # f"Type 'yes' to confirm and launch the job."
        )

        confirmation = await self.ask(context, "Is this correct? (yes/no)")
        if confirmation and confirmation.lower() == "yes":
            # Here, you would include the code to actually launch the job with the given parameters
            # Simulate launching the job

            job_response = await self.external_api_handler.launch_job(
                api_key,
                requesterTitle,
                submissionsRequired,
                requesterDescription,
                fundAmount,
                network_chain_id,
            )
            if job_response:
                # If the job was launched successfully, do something with the response

                self.job_queue.append(
                    {
                        "result_channel_id": result_channel_id,
                        "job_id": job_response,  # Store the job ID
                        "api_key": api_key,
                    }
                )
                await context.send(f"Job launched successfully: {job_response}")
            else:
                # If there was an error launching the job, inform the user
                await context.send("There was an error launching the job.")
        else:
            await context.send("Job launch cancelled.")

    async def ask(self, context, question):
        await context.send(question)
        try:
            message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == context.author
                and m.channel == context.channel,
                timeout=60.0,  # Waits for 60 seconds
            )
        except asyncio.TimeoutError:
            await context.send("Sorry, you didn't reply in time!")
            return None
        return message.content


async def setup(bot):
    job_launcher_cog = JobLauncher(bot)
    await bot.add_cog(job_launcher_cog)  # Use 'await' to properly await the coroutine
    job_launcher_cog.publish_results.start()  # Start the background task when the cog is loaded
