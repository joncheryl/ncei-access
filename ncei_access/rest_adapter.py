# John Sherrill
# June 2025
"""
Low level components of NCEI Access API wrapper.
"""

from typing import Dict
import logging
from json import JSONDecodeError
import requests
import requests.packages
from ncei_access.exceptions import NceiAccessException
from ncei_access.models import Result


class RestAdapter:
    """Low level tool for accessing API."""

    def __init__(
        self,
        hostname: str = "www.ncei.noaa.gov/access/services",
        logger: logging.Logger = None,
    ):
        """
        :param hostname: Normally, www.ncei.noaa.gov/access/services, defaults to "www.ncei.noaa.gov/access/services"
        :param ver: Currectly only v1, defaults to "v1"
        :param logger: (optional) If your app has a logger, pass it in here. Defaults to None
        """#pylint: disable=line-too-long

        self.url = f"https://{hostname}/"
        self._logger = logger or logging.getLogger(__name__)

    def get(self, endpoint: str = "data/v1/", ep_params: Dict = None) -> Result:
        """Fundamental function for getting data.

        :param endpoint: 4 options: - "data/v1" for getting data. - "search/v1/data" for searching for stations or dataTypes. - "support/v3/datasets" to discover metadata about datasets. - "orders/v1" to retrieve information about previous orders. Idk.
        :param ep_params: parameters for API call, defaults to None
        :raises NceiAccessException: _description_
        :raises NceiAccessException: _description_
        :raises NceiAccessException: _description_
        :return: _description_
        """#pylint: disable=line-too-long
        if ep_params is None:
            ep_params = {}

        full_url = f"{self.url}{endpoint}"

        # API quirk 1: force format=json for 'data' endpoint
        if endpoint == "data/v1/":
            ep_params.setdefault("format", "json")

        self._logger.debug(f"url={full_url}, params={ep_params}")

        try:
            response = requests.get(url=full_url, params=ep_params, timeout=10)
        except requests.exceptions.RequestException as e:
            self._logger.error(msg=f"Request failed: {e}")
            raise NceiAccessException("Request failed") from e

        try:
            data_out = response.json()
        except (ValueError, JSONDecodeError) as e:
            self._logger.error(
                f"url={full_url}, params={ep_params}, success=False, message={e}"
            )
            raise NceiAccessException("Bad JSON in response") from e

        # Return result if status code indicates success
        is_success = 200 <= response.status_code <= 299
        message = response.reason
        status_code = response.status_code

        # API quirk 2: for search endpoint, results are nested under "results"
        result_data = (
            data_out.get("results", data_out)
            if endpoint == "search/v1/data"
            else data_out
        )

        log_msg = (
            f"url={full_url}, params={ep_params}, success={is_success}, "
            f"status_code={status_code}, message={message}"
        )

        if is_success:
            self._logger.debug(log_msg)
            return Result(status_code, message=message, data=result_data)

        self._logger.error(log_msg)
        raise NceiAccessException(f"{status_code}: {message}")
