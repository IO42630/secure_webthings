# Local imports with implicit path.
import sys
from os import path, pardir
sys.path.append(path.join(path.dirname(path.abspath(__file__)), pardir))

from ecdsa import SigningKey, VerifyingKey
from ace.authz.authorization_server import Grant


HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

AS_IDENTITY = SigningKey.from_der(
        bytes.fromhex('30770201010420fb37dbd38e48cfc41475e50dd52d7328102bd31cf881e4'
                'e163c58e5f150aa1f2a00a06082a8648ce3d030107a144034200047069be'
                'd49cab8ffa5b1c820271aef0bc0c8f5cd149e05c5b9e37686da06d02bd5f'
                '7bc35ea8265be7c5e276ad7e7d0eb05e4a0551102a66bba88b02b5eb4c33'
                '55'
                )
        )

AS_PUBLIC_KEY: VerifyingKey = VerifyingKey.from_der(
        bytes.fromhex("3059301306072a8648ce3d020106082a8648ce3d030107034200047069be"
                "d49cab8ffa5b1c820271aef0bc0c8f5cd149e05c5b9e37686da06d02bd5f"
                "7bc35ea8265be7c5e276ad7e7d0eb05e4a0551102a66bba88b02b5eb4c33"
                "55"
                )
        )

RS_IDENTITY: SigningKey = SigningKey.from_der(
        bytes.fromhex("307702010104200ffc411715d3cc4917bd27ac4f310552b085b1ca0bb0a8"
                "bbb9d8931d651544c1a00a06082a8648ce3d030107a144034200046cc415"
                "12d92fb03cb3b35bed5b494643a8a8a55503e87a90282c78d6c58a7e3c88"
                "a21c0287e7e8d76b0052b1f1a2dcebfea57714c1210d42f17b335adcb76d"
                "7a"
                )
        )

RS_PUBLIC_KEY: VerifyingKey = VerifyingKey.from_der(
        bytes.fromhex('3059301306072a8648ce3d020106082a8648ce3d030107034200046cc415'
                '12d92fb03cb3b35bed5b494643a8a8a55503e87a90282c78d6c58a7e3c88'
                'a21c0287e7e8d76b0052b1f1a2dcebfea57714c1210d42f17b335adcb76d'
                '7a'
                )
        )

CLIENT_ID = 'ace_client_1'
CLIENT_SECRET = b'ace_client_1_secret_123456'

LOCALHOST: str = 'localhost'
PI_HOST: str = '192.168.43.17'
COAP_PI_HOST: str = '::'

AS_PORT: str = 8088
PC_AS_URL = 'http://' + LOCALHOST + ':' + str(AS_PORT)
PI_AS_URL = 'http://' + PI_HOST + ':' + str(AS_PORT)

ACE_HTTP_RS_PORT: str = 8082
PC_ACE_HTTP_RS_URL = 'http://' + LOCALHOST + ':' + str(ACE_HTTP_RS_PORT)
PI_ACE_HTTP_RS_URL = 'http://' + PI_HOST + ':' + str(ACE_HTTP_RS_PORT)
ACE_COAP_RS_PORT: int = 8086
PC_ACE_COAP_RS_URL = 'coap://' + LOCALHOST + ':' + str(ACE_COAP_RS_PORT)
PI_ACE_COAP_RS_URL = 'coap://' + PI_HOST + ':' + str(ACE_COAP_RS_PORT)


AUDIENCE = 'rpi_thing'
SCOPES = ['GET /',
          'GET / ',
          'GET /properties',
          'GET /properties/led',
          'POST /properties/led',
          'GET /properties/temperature',
          'POST /properties/temperature',
          'GET /properties/humidity',
          'POST /properties/humidity',
          'GET /properties/pressure',
          'POST /properties/pressure',
          'GET /properties/proximity',
          'POST /properties/proximity',
          'GET /properties/text',
          'POST /properties/text',
          'GET /actions',
          'POST /actions',
          'GET /actions/switch_led',
          'POST /actions/switch_led',
            'GET /actions/set_text',
          'POST /actions/set_text',
          'GET /events',
          'GET /events/proximity']

GRANTS = [Grant(audience = AUDIENCE, scopes = SCOPES), ]
