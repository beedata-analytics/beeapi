import functools
import logging

from datetime import datetime
from datetime import timedelta
from json import dumps

import requests.exceptions
import urllib3

from requests import Session
from requests import request
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


__version__ = "0.2.0"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Client(object):
    class Decorators(object):
        @classmethod
        def authorize_on_expire(cls, func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                obj = args[0]
                result = None
                try:
                    result = func(*args, **kwargs)
                    result.raise_for_status()

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code in [401, 500]:
                        # token expired/unexpected server error => reset token and retry
                        obj.cookie = None
                        result = func(*args, **kwargs)

                return result

            return wrapper

    def __init__(self, config):
        self.cookie = None
        self.config = config
        self.http_headers = {
            "Content-type": "application/json",
            "X-CompanyId": str(self.config["company_id"]),
        }

        self.certificate = (
            self.config["auth"]["cert_file"],
            self.config["auth"]["key_file"],
        )
        self.company_id = self.config["company_id"]
        self.base_url = self.config["base_url"]
        self.endpoints = self.config["endpoints"]
        self.username = self.config["auth"]["username"]
        self.password = self.config["auth"]["password"]

    def _do_login(self):
        data = {"username": self.username, "password": self.password}
        response = request(
            "POST",
            self.base_url + "/authn/login",
            data=dumps(data),
            headers=self.http_headers,
            verify=False,
        )
        self.cookie = {"iPlanetDirectoryPro": response.json()["token"]}
        return self.cookie

    def _do_logout(self):
        request(
            "GET",
            self.base_url + "/authn/logout",
            cookies=self.cookie,
            headers=self.http_headers,
            verify=False,
        )


    @Decorators.authorize_on_expire
    def _get_contract(self, contract_id):

        response = request(
            "GET",
            self.base_url + self.endpoints["contracts"] + "/%s" % contract_id,
            cookies=self.cookie or self._do_login(),
            headers=self.http_headers,
            cert=self.certificate,
            verify=False,
        )

        return response

    @Decorators.authorize_on_expire
    def _send_data(self, data, data_type):
        s = Session()
        retries = Retry(
            total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
        )
        s.mount("https://", HTTPAdapter(max_retries=retries))
        response = s.post(
            self.base_url + self.endpoints[data_type],
            cookies=self.cookie or self._do_login(),
            headers=self.http_headers,
            cert=self.certificate,
            verify=False,
            data=dumps(data),
        )

        return response

    @Decorators.authorize_on_expire
    def _modify_contract(self, data):
        response = request(
            "GET",
            self.base_url
            + self.endpoints["contracts"]
            + "/%s" % data["contractId"],
            cookies=self.cookie or self._do_login(),
            headers=self.http_headers,
            cert=self.certificate,
            verify=False,
        )
        response = response.json()

        if "_etag" in response:
            headers = {
                "Content-type": "application/json",
                "X-CompanyId": str(self.company_id),
                "If-Match": response["_etag"],
            }
            response = request(
                "PATCH",
                self.base_url
                + self.endpoints["contracts"]
                + "/%s" % data["contractId"],
                cookies=self.cookie or self._do_login(),
                headers=headers,
                cert=self.certificate,
                verify=False,
                data=dumps(data),
            )
        else:
            response = request(
                "POST",
                self.base_url + self.endpoints["contracts"],
                cookies=self.cookie or self._do_login(),
                headers=self.http_headers,
                cert=self.certificate,
                verify=False,
                data=dumps(data),
            )

        return response

    @Decorators.authorize_on_expire
    def put_measures(self, data):
        response = request(
            "POST",
            self.base_url + self.endpoints["measures"],
            cookies=self.cookie or self._do_login(),
            headers=self.http_headers,
            cert=self.certificate,
            verify=False,
            data=dumps(data),
        )

        return response

    @Decorators.authorize_on_expire
    def put_tertiary(self, data):
        response = request(
            "POST",
            self.base_url + self.endpoints["tertiary"],
            cookies=self.cookie or self._do_login(),
            headers=self.http_headers,
            cert=self.certificate,
            verify=False,
            data=dumps(data),
        )

        return response

    @Decorators.authorize_on_expire
    def put_tou(self, data):
        response = request(
            "POST",
            self.base_url + self.endpoints["tou"],
            cookies=self.cookie or self._do_login(),
            headers=self.http_headers,
            cert=self.certificate,
            verify=False,
            data=dumps(data),
        )

        return response

    @Decorators.authorize_on_expire
    def put_community(self, data):
        response = request(
            "POST",
            self.base_url + self.endpoints["community"],
            cookies=self.cookie or self._do_login(),
            headers=self.http_headers,
            cert=self.certificate,
            verify=False,
            data=dumps(data),
        )

        return response

    def upload_contract(self, data):
        """Function to decide when contract needs to be POST, PATCH or nothing

        :param data: contract document with all needed information
        """
        contract_report = {}
        if self._get_contract(data["document"]["contractId"]):
            logger.debug(
                "Contract [%s] already on Beedata API. "
                "Proceeding with a PATCH operation"
                % data["document"]["contractId"]
            )
            res = self._modify_contract(data["document"])
            contract_report["contracts_api_call"] = "PATCH"
            contract_report["contracts_api_status"] = res.status_code
            if res.status_code != 200:
                contract_report["contracts_api_error"] = res.text
                logger.error(
                    "Beedata API response was unexpected on PATCH "
                    "existing contract [%s]: %s"
                    % (data["document"]["contractId"], res.text)
                )
            else:
                logger.info(
                    "PATCH contract [%s] successfully modified "
                    "on Beedata API." % (data["document"]["contractId"])
                )
        else:
            logger.debug(
                "POST new contract [%s] to Beedata"
                % (data["document"]["contractId"])
            )
            res = self._send_data(data["document"], "contracts")
            contract_report["contracts_api_call"] = "POST"
            contract_report["contracts_api_status"] = res.status_code
            if res.status_code != 201:
                contract_report["contracts_api_error"] = res.text
                logger.error(
                    "Beedata API response was unexpected on POST new "
                    "contract [%s]:    %s"
                    % (data["document"]["contractId"], res.text)
                )
            else:
                logger.info(
                    "New contract [%s] successfully created "
                    "on Beedata API." % (data["document"]["contractId"])
                )

        return contract_report

    @staticmethod
    def date_converter(dt, format, last_second=False, str_format=None):
        """Convert a string into datetime object or another string with format changes

        :param dt: datetime string
        :param format: format to parse dt
        :param last_second: if we need to transform a day date into last
        moment of that day
        :param str_format: if we need to transform datetime into string again
        """
        ts = datetime.strptime(dt, format)
        if last_second:
            ts = ts + timedelta(days=1) - timedelta(seconds=1)

        if str_format:
            ts = ts.strftime(str_format)

        return ts
