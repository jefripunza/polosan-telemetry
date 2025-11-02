import uasyncio as asyncio

async def loop1():
    i = 0
    while True:
        i += 1
        print(f"Loop 1 jalan: {i}")
        await asyncio.sleep(1)  # jeda 1 detik

async def loop2():
    i = 0
    while True:
        i += 1
        print(f"Loop 2 jalan: {i}")
        await asyncio.sleep(2)  # jeda 2 detik

async def loop3():
    i = 0
    while True:
        i += 1
        print(f"Loop 3 jalan: {i}")
        await asyncio.sleep(3)  # jeda 3 detik

async def main():
    await asyncio.gather(loop1(), loop2(), loop3())

asyncio.run(main())
