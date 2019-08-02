# Create implicit path.
import sys
from os import path, pardir
sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir, pardir))

# External imports.
import asyncio
from aiohttp import web

from ace.authz.authorization_server import AuthorizationServer

# Internal imports.
from webthing_ace_tornado.parameters import *



def main():
    # Provision Authorization Server .
    loop = asyncio.get_event_loop()
    app = web.Application(loop = loop)
    server = AuthorizationServer(AS_IDENTITY, app.router)

    # Pre-register Resource Server .
    server.register_resource_server(audience = AUDIENCE,
                                    scopes = SCOPES,
                                    public_key = RS_PUBLIC_KEY
                                    )

    # Pre-register Client .
    server.register_client(client_id = CLIENT_ID,
                           client_secret = CLIENT_SECRET,
                           grants = GRANTS
                           )

    # Launch Server App .
    web.run_app(app,
                host = LOCALHOST,
                port = AS_PORT)


if __name__ == "__main__":
    main()
