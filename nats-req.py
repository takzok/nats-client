import argparse, sys
import asyncio
from nats.aio.client import Client as NATS

async def run(loop):
    parser = argparse.ArgumentParser()

    # e.g. nats-req hello -d "world" -s nats://127.0.0.1:4222 -s nats://127.0.0.1:4223
    parser.add_argument('subject', default='hello', nargs='?')
    parser.add_argument('-m', '--message', default="hello nats world")
    parser.add_argument('-s', '--servers', default=[], action='append')
    args = parser.parse_args()

    nc = NATS()

    async def error_cb(e):
        print("Error:", e)

    async def closed_cb():
        print("Connection to NATS is closed.")

    async def reconnected_cb():
        print("Connected to NATS at {}...".format(nc.connected_url.netloc))

    async def sub(msg):
      print("Received a message on '{subject} {reply}': {message}".format( subject=msg.subject, reply=msg.reply, message=msg.data.decode()))
      rep_msg = "Reply message: received message is '{data}'".format(data=msg.data.decode())
      await nc.publish(msg.reply, rep_msg.encode())

    options = {
        "io_loop": loop,
        "error_cb": error_cb,
        "closed_cb": closed_cb,
        "reconnected_cb": reconnected_cb
    }

    try:
        if len(args.servers) > 0:
            options['servers'] = args.servers

        await nc.connect(**options)
    except Exception as e:
        print(e)

    print("Connected to NATS at {}...".format(nc.connected_url.netloc))

    # wait message on request subject
    await nc.subscribe(args.subject, cb=sub)

    try:
      msg = await nc.request(args.subject, args.message.encode(), timeout=1)
      print("reply message on '{reply}': {message}".format(reply=msg.subject, message=msg.data.decode()), )
    except asyncio.TimeoutError:
      print('Timed out waiting for massage')
    await nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(loop))
    finally:
        loop.close()