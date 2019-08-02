# Local imports with implicit path.
import sys
from os import path, pardir
# sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir))


# replace 'localhost' with custom url as needed. e.g. 'http://192.168.43.17:8081'
HOST: str = 'localhost'
PLAIN_HTTP_RS_PORT: str = 8081
PLAIN_HTTP_RS_URL = 'http://' + HOST + ':' + str(PLAIN_HTTP_RS_PORT)

HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
