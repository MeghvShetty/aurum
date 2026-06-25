import asyncio, ssl, certifi, aiohttp


async def test():
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.load_verify_locations("/Users/meghshetty67ss7687/Desktop/herald/caBundle/rootCA.pem")
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ctx)) as s:
        async with s.get("https://localhost:8080/health") as r:
            print(r.status, await r.text())

asyncio.run(test())
