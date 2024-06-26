# 
# Copyright (c) 2024 Gabriel Freitas: gabriel.estudy.reis@gmail.com
#

from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse

import aio_pika
import asyncio

from libmessage import *
from librabbitmq import *

app = FastAPI()

@app.get("/")
def read_root():
	return {"Hello": "World"}

async def unittest_feed_event_generator(request: Request):
# {
	connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
	channel = await connection.channel()
	queue = await channel.declare_queue("unittest")

	try:
		async with queue.iterator() as queue_iter:
			async for message in queue_iter:
				async with message.process():
					# Yield the message payload as SSE event
					yield {"data": message.body.decode()}

	except asyncio.CancelledError:
		await channel.close()
		await connection.close()
# }

@app.get("/feed")
async def unittest_feed(request: Request):
	event_generator = unittest_feed_event_generator(request)
	return EventSourceResponse(event_generator)

@app.post("/runtests")
def runtests():
	command = "runtests"
	origin = "unittestapi"
	msg = generate_command_message(command, origin)

	sender = rabbitmq_new_sender("test_queue")
	sender.send_message(msg)

	return {"success": True}
