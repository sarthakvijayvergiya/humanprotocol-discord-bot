"""
Author Sarthak Vijayvergiya - https://github.com/sarthakvijayvergiya
Description: A Discord bot that helps in launching jobs, setting API keys, and configuring result channels for the Human Protocol.
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
import asyncio
from discord.ext import tasks
from datetime import datetime
import os
import json
from services.external_api_handler import ExternalAPIHandler


class JobLauncher(commands.Cog, name="JobLauncher"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.job_queue = []  # A list to keep track of jobs to publish results for
        self.track_escrow_queue = asyncio.Queue()  # New queue for escrow ID retrieval
        self.external_api_handler = ExternalAPIHandler()
        self.result_check_interval = int(
            os.getenv("RESULT_CHECK_INTERVAL", 180)
        )  # Default to 180 seconds
        self.allowed_api_key = os.getenv('USER_API_KEY')
        self.whitelisted_channel = os.getenv("WHITELISTED_CHANNEL")


    def cog_unload(self):
        self.publish_results.cancel()  # Cancel the background task when the cog is unloaded
        self.external_api_handler.close_session()

    @tasks.loop(seconds=60)  # Run this loop every minute
    async def escrow_id_retrieval_worker(self):
        current_time = datetime.datetime.utcnow()
        jobs_to_remove = []  # List to keep track of jobs to remove from the queue

        for job in self.job_queue:
            time_since_launch = (current_time - job['launch_time']).total_seconds()
            # Check if at least 12 minutes have passed since the job was launched
            if time_since_launch >= 720 and time_since_launch % 720 < 60:
                job_details = await self.external_api_handler.get_job_details(job["api_key"], job["job_id"])
                if job_details and 'escrow_id' in job_details:
                    job['escrow_id'] = job_details['escrow_id']
                    await self.track_escrow_queue.put(job)  # Move to the tracking queue
                    jobs_to_remove.append(job)  # Mark this job for removal from the queue

        # Remove the processed jobs from the job_queue
        for job in jobs_to_remove:
            self.job_queue.remove(job)

    @escrow_id_retrieval_worker.before_loop
    async def before_escrow_id_retrieval_worker(self):
        await self.bot.wait_until_ready()  # Ensure the bot is ready before starting the loop


    @tasks.loop(
        seconds=60
    )  # Temporary interval, will be reset in before_publish_results
    async def publish_results(self):
        for job in self.job_queue:
            results = await self.external_api_handler.check_job_result(
                self.allowed_api_key, job["job_id"]
            )
            if results:
                # Assuming that the job is considered complete if any results are returned
                result_channel = self.whitelisted_channel
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

    async def check_whitelisted_channel(self, context: Context):
        # Check if the command was used in a private or DM channel
        if isinstance(context.channel, discord.DMChannel):
            await context.send("This command is not allowed in private messages or DMs.")
            return

        # Check if the channel is the whitelisted channel
        whitelisted_channel = os.getenv("WHITELISTED_CHANNEL")
        if (
            context.channel.name != whitelisted_channel
            and str(context.channel.id) != whitelisted_channel
        ):
            await context.send("This command is not allowed in this channel.")
            return
        return True
    
    @commands.command(name="listjobs")
    @commands.check(commands.has_role("Viewer"))
    async def list_jobs(self, ctx, status: str='PENDING', limit: int=10, skip: int=0):
        # Check the whitelisted channel before executing the command
        if not await self.check_whitelisted_channel(ctx):
            return
        
        # Parse the supported networks from the environment variable
        supported_networks_str = os.getenv("SUPPORTED_NETWORKS", "{}")
        supported_networks = json.loads(supported_networks_str)
        
        # Ask the user to select a network
        network_choices = ", ".join(supported_networks.keys())
        network_choice_message = await self.ask(ctx, f"Select a network: {network_choices}")
        
        # Validate the user's choice
        if not network_choice_message or network_choice_message.content not in supported_networks:
            await ctx.send("Invalid network selection. Job listing cancelled.")
            return
        
        network_chain_id = supported_networks[network_choice_message.content]
        networks = [network_chain_id]  # Convert the choice to a list as the API expects a list
        
        # Call the API handler to list pending jobs
        try:
            pending_jobs = await self.bot.external_api_handler.list_pending_jobs(api_key, networks, status, limit, skip)
            if pending_jobs is not None:
                # Send the list of pending jobs to the user via DM
                await ctx.author.send(f"Pending Jobs: {json.dumps(pending_jobs, indent=2)}")
            else:
                await ctx.author.send("Failed to retrieve pending jobs.")
        except Exception as e:
            await ctx.author.send(f"An error occurred: {str(e)}")

    @commands.command(name="launchJob")
    @commands.has_role("Launcher")
    async def launch_job(self, context: Context):
         # Check the whitelisted channel before executing the command
        if not await self.check_whitelisted_channel(context):
            return

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
                self.allowed_api_key,
                requesterTitle,
                submissionsRequired,
                requesterDescription,
                fundAmount,
                network_chain_id,
            )
            if job_response:
                # If the job was launched successfully, do something with the response

                self.jobs_ids_queue.append(
                    {
                        "job_id": job_response,
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
