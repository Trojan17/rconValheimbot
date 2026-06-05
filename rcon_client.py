import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from mcrcon import MCRcon

_executor = ThreadPoolExecutor(max_workers=4)


def _run(command: str) -> str:
    host = os.getenv('RCON_HOST')
    port = int(os.getenv('RCON_PORT', '2457'))
    password = os.getenv('RCON_PASSWORD')
    if not host or not password:
        raise RuntimeError('RCON_HOST and RCON_PASSWORD must be configured')
    with MCRcon(host, password, port=port, timeout=15) as mcr:
        return mcr.command(command) or '(no response)'


async def rcon(command: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _run, command)
