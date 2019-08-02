'''
Credit to `https://edmundmartin.com/aiohttp-background-tasks/`
'''
import asyncio
from aiohttp import web




class BackgroundAuthorizationServer():


     def __init__(self):
         self.loop = asyncio.get_event_loop()



     def run_app(self):
         loop = self.loop
         # app = loop.run_until_complete(self.create_app())
         # app.on_startup.append(self.start_background_tasks)
         # app.on_cleanup.append(self.cleanup_background_tasks)
         # web.run_app(app, host = self.host, port = self.port)