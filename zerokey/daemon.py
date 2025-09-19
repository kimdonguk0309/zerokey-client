import asyncio, os, signal, sys
from zerokey.core import ZKChannel
from zerokey.tunnel import SocksServer

async def handshake(relay: str, pwd: str) -> bytes:
    host, port = relay.rsplit(":", 1)
    reader, writer = await asyncio.open_connection(host, int(port))
    zk = ZKChannel(pwd)

    # 1) client hello
    hello, client_kyber_sk = zk.client_hello(b"")  # server_pk는 서버가 주도록 개선
    writer.write(json.dumps(hello).encode() + b"\n")
    await writer.drain()

    # 2) server response
    rsp = json.loads((await reader.readline()).decode())
    session_key = zk.client_finish(rsp, client_kyber_sk)
    return session_key, reader, writer

async def keepalive_tunnel(relay: str, pwd: str):
    while True:
        try:
            key, *_ = await handshake(relay, pwd)
            await SocksServer(key, *relay.rsplit(":", 1)).start()
        except Exception as e:
            print("reconnect in 5s:", e)
            await asyncio.sleep(5)

def start_daemon(relay: str, pwd: str):
    if not pwd:
        import getpass
        pwd = getpass.getpass("ZeroKey password: ")
    asyncio.run(keepalive_tunnel(relay, pwd))
