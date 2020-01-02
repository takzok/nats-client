import asyncio
import argparse
from nats.aio.client import Client as NATS


async def run(loop):
    parser = argparse.ArgumentParser()

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
    await nc.publish(args.subject, args.message.encode())
    await nc.flush()
    await nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(loop))
    finally:
        loop.close()