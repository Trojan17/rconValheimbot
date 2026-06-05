import asyncio
import os
import struct

_TIMEOUT = 15
_TYPE_LOGIN = 3
_TYPE_COMMAND = 2


def _pack(request_id: int, pkt_type: int, body: str) -> bytes:
    payload = body.encode('utf-8') + b'\x00\x00'
    header = struct.pack('<ii', request_id, pkt_type)
    return struct.pack('<i', len(header) + len(payload)) + header + payload


async def _read_packet(reader: asyncio.StreamReader) -> tuple[int, int, str]:
    size_data = await reader.readexactly(4)
    size = struct.unpack('<i', size_data)[0]
    data = await reader.readexactly(size)
    req_id, pkt_type = struct.unpack('<ii', data[:8])
    body = data[8:-2].decode('utf-8', errors='replace')
    return req_id, pkt_type, body


async def rcon(command: str) -> str:
    host = os.getenv('RCON_HOST')
    port = int(os.getenv('RCON_PORT', '2457'))
    password = os.getenv('RCON_PASSWORD')
    if not host or not password:
        raise RuntimeError('RCON_HOST and RCON_PASSWORD must be configured')

    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port), timeout=_TIMEOUT
    )
    try:
        writer.write(_pack(1, _TYPE_LOGIN, password))
        await writer.drain()
        req_id, _, _ = await asyncio.wait_for(_read_packet(reader), timeout=_TIMEOUT)
        if req_id == -1:
            raise RuntimeError('RCON authentication failed — wrong password')

        writer.write(_pack(2, _TYPE_COMMAND, command))
        await writer.drain()
        _, _, body = await asyncio.wait_for(_read_packet(reader), timeout=_TIMEOUT)
        return body or '(no response)'
    finally:
        writer.close()
        await writer.wait_closed()
