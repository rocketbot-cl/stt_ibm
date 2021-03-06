# coding: utf-8

# Copyright 2019 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import jwt
import time
import requests
from .api_exception import ApiException


class JWTTokenManager(object):

    def __init__(self, url, disable_ssl_verification=False, token_name=None):
        """
        :attr str url: url of the API to retrieve tokens from
        :attr bool disable_ssl_verification: disables ssl verification when True
        :attr: str token_name: name of the key containing the token
        """
        self.url = url
        self.disable_ssl_verification = disable_ssl_verification
        self.token_name = token_name
        self.token_info = {}
        self.time_for_new_token = None
        self.http_config = {}

    def get_token(self):
        """
        The source of the token is determined by the following logic:
        2.  a) If this class does not yet have one, make a request for one
            b) If this class token has expired, request a new one
        3. If this class is managing tokens and has a valid token stored, send it

        Returns
        -------
        str
            A valid access token
        """
        if not self.token_info or self._is_token_expired():
            token_response = self.request_token()
            self._save_token_info(token_response)

        return self.token_info.get(self.token_name)

    def set_disable_ssl_verification(self, status=False):
        """
        Sets the ssl verification to enabled or disabled
        """
        self.disable_ssl_verification = status

    def request_token(self):
        raise NotImplementedError(
            'request_token MUST be overridden by a subclass of JWTTokenManager.'
        )

    def _get_current_time(self):
        return int(time.time())

    def _is_token_expired(self):
        """
        Check if currently stored token is expired.

        Using a buffer to prevent the edge case of the
        oken expiring before the request could be made.

        The buffer will be a fraction of the total TTL. Using 80%.

        Returns
        -------
        bool
            If token expired or not
        """
        if not self.time_for_new_token:
            return True

        current_time = self._get_current_time()
        return self.time_for_new_token < current_time

    def _save_token_info(self, token_response):
        """
        Decode the access token and save the response from the JWT service to the object's state

        Parameters
        ----------
        token_response : str
            Response from token service
        """
        access_token = token_response.get(self.token_name)

        # The time of expiration is found by decoding the JWT access token
        decoded_response = jwt.decode(access_token, verify=False)
        exp = decoded_response.get('exp')
        iat = decoded_response.get('iat')

        # exp is the time of expire and iat is the time of token retrieval
        time_to_live = exp - iat
        expire_time = exp
        fraction_of_ttl = 0.8
        self.time_for_new_token = expire_time - (time_to_live *
                                                 (1.0 - fraction_of_ttl))
        self.token_info = token_response

    def _request(self,
                 method,
                 url,
                 headers=None,
                 params=None,
                 data=None,
                 auth_tuple=None,
                 **kwargs):
        kwargs = dict({"timeout": 60}, **kwargs)
        kwargs = dict(kwargs, **self.http_config)

        if self.disable_ssl_verification:
            kwargs['verify'] = False

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            auth=auth_tuple,
            **kwargs)
        if 200 <= response.status_code <= 299:
            return response.json()
        else:
            raise ApiException(response.status_code, http_response=response)
