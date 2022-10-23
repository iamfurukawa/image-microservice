import requests
import jwt
from base64 import b64encode
import logging as logger

#BASE_URL = 'http://localhost:6660'
BASE_URL = 'http://oauth2-server:6660'


def authenticate(token):
    logger.error('m=authenticate stage=init token={}'.format(token))

    if token == '' or token is None:
        return False

    url = "{}/validate".format(BASE_URL)
    headers = {'Authorization': 'Bearer {}'.format(token)}
    response = requests.request("POST", url, headers=headers, data={})

    token_decoded = jwt.decode(token, options={"verify_signature": False}, algorithms="HS256")

    isValid = response.status_code == 204 and (token_decoded['scope'] == 'image-ms' or token_decoded['scope'] == 'full')
    logger.error('m=authenticate stage=end isValid={}'.format(isValid))
    return isValid


def sign_in(client_id, client_secret):
    logger.error('m=sign_in stage=init client_id={} client_secret={}'.format(
        client_id, client_secret))
    url = "{}/login".format(BASE_URL)
    basic_token = "{}:{}".format(client_id, client_secret)
    basic_token = b64encode(str.encode(basic_token)).decode("ascii")
    headers = {'Authorization': 'Basic {}'.format(basic_token)}
    response = requests.request("POST", url, headers=headers, data={})

    if response.status_code == 200:
        responseJson = response.json()
        token = responseJson['access_token']
        logger.error('m=sign_in stage=end token={}'.format(token))
        isValid = authenticate(token)

        if isValid == False:
            logger.error('m=sign_in stage=end invalid token')
            return None

        return token

    logger.error('m=sign_in stage=end failed to sign in')
    return None
