import asyncio

async def time_checker():
    while True:
        await asyncio.sleep(1)
        print("the time has come")

# ioloop = asyncio.get_event_loop()
# timers = [ioloop.create_task(time_checker())]

# print("before run")
# asyncio.run(time_checker())
# print("after run")

asyncio.create_task(time_checker())