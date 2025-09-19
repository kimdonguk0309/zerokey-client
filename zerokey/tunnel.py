import asyncio, struct, socket
from zerokey.core import ZKChannel

LOCAL_SOCKS_PORT = 1080

class SocksServer:
    def __init__(self, session_key: bytes, relay_host: str, relay_port: int):
        self.box = ZKChannel("").make_box(session_key)
        self.relay = (relay_host, relay_port)

    async def handle_client(self, reader, writer):
        # SOCKS5 handshake
        ver, nmethods = struct.unpack("!BB", await reader.read(2))
        await reader.read(nmethods)
        writer.write(b"\x05\x00")  # no auth
        await writer.drain()

        # CONNECT request
        ver, cmd, _, atyp = struct.unpack("!BBBB", await reader.read(4))
        if cmd != 1:  # only CONNECT
            writer.close(); return
        if atyp == 1:   # IPv4
            addr = socket.inet_ntoa(await reader.read(4))
        elif atyp == 3: # domain
            dom_len = (await reader.read(1))[0]
            addr = (await reader.read(dom_len)).decode()
        port = struct.unpack("!H", await reader.read(2))[0]

        # relay open
        rr, rw = await asyncio.open_connection(*self.relay)
        # send encrypted target info
        payload = f"{addr}:{port}".encode()
        nonce = os.urandom(24)
        enc = self.box.encrypt(payload, nonce)
        rw.write(nonce + enc)
        await rw.drain()

        # bidirectional copy
        async def pipe(a, b):
            while data := await a.read(8192):
                b.write(data); await b.drain()
        await asyncio.gather(pipe(reader, rw), pipe(rr, writer))
        writer.close(); rr.close()

    async def start(self):
        srv = await asyncio.start_server(self.handle_client, "127.0.0.1", LOCAL_SOCKS_PORT)
        async with srv: await srv.serve_forever()
