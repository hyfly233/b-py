import asyncclick as click
import asyncio
import base64
import os
import urllib
from uuid import uuid4



@click.command()
@click.option("--agent", default="http://localhost:10000")
@click.option("--session", default=0)
@click.option("--history", default=False)
@click.option("--use_push_notifications", default=False)
@click.option("--push_notification_receiver", default="http://localhost:5000")
async def cliMain(agent, session, history, use_push_notifications: bool, push_notification_receiver: str):
    pass