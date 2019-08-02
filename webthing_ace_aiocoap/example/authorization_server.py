# External imports.
import asyncio

from ace.authz.authorization_server import AuthorizationServer
from aiohttp import web

# Internal imports.
from webthing_ace_aiocoap.parameters import *


def main():
    # Provision private key of authorization server
    loop = asyncio.get_event_loop()
    app = web.Application(loop = loop)
    server = AuthorizationServer(AS_IDENTITY,
                                 app.router)

    # Pre-register Resource Server
    server.register_resource_server(audience = AUDIENCE,
                                    scopes = SCOPES,
                                    public_key = RS_PUBLIC_KEY)

    # Pre-register Client for WT-aioCoAP demo.
    server.register_client(client_id = CLIENT_ID,
                           client_secret = CLIENT_SECRET,
                           grants = GRANTS)

    # Launch Server.
    web.run_app(app,
                host = LOCALHOST,
                port = AS_PORT)


if __name__ == "__main__":
    main()
