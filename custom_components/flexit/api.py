"""Asynchronous Python client for Flexit."""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import urllib.parse
from aiohttp.client import ClientSession
from aiohttp.client_reqrep import ClientResponse

from homeassistant.const import HTTP_OK

from .const import (
    AWAY_AIR_TEMPERATURE_PATH,
    DATAPOINTS_PATH,
    DEVICE_INFO_PATH_LIST,
    ELECTRIC_HEATER_PATH,
    FILTER_PATH,
    HOME_AIR_TEMPERATURE_PATH,
    LOGGER,
    MODE_AWAY,
    MODE_HIGH,
    MODE_HOME,
    PLANTS_PATH,
    SENSOR_DATA_PATH_LIST,
    SUBSCRIPTION_KEY,
    TOKEN_PATH,
    VENTILATION_MODE_PUT_PATH,
)

from .models import (
    FlexitDeviceInfo,
    FlexitPlantItem,
    FlexitPlants,
    FlexitSensorsResponse,
    FlexitSensorsResponseStatus,
    FlexitToken,
)


RESULT_SUCCESS = "Success"


class FlexitApiClient:
    """Main class for handling connections with a Flexit unit."""

    def __init__(
        self,
        session: ClientSession,
        username: str,
        password: str,
        plant_id: str or None = None,
    ) -> None:
        """Initialize connection with the Flexit."""
        self._session = session
        self._username = username
        self._password = password
        self._plant_id = plant_id

        self.token: str or None = None
        self.token_refreshdate: date = date.today()

    def path(self, path: str) -> str:
        """Return path with plant_id prefixed."""

        if self._plant_id is None:
            LOGGER.warning("plant_id=%s", self._plant_id)

        return f"{self._plant_id}{path}"

    async def handle_request(self, response: ClientResponse) -> Any:
        """Get request."""

        LOGGER.debug("handle_request=%s", response)

        async with response as resp:

            if resp.status != HTTP_OK:
                raise Exception(f"Response not HTTP_OK {resp}")

            data = await resp.json()

        return data

    async def get(self, path: str) -> Any:
        """Get request."""

        LOGGER.debug("get=%s", path)

        return await self.get_url(self.get_escaped_filter_url(path))

    async def get_url(self, url: str) -> Any:
        """Get request."""

        LOGGER.debug("get_url=%s", url)

        return await self.handle_request(
            await self._session.get(
                url=url,
                headers=self.get_headers_with_token(self.token),
            )
        )

    async def put(self, path: str, body: Any) -> Any:
        """Put request."""

        LOGGER.debug("put=%s, body=%s", path, body)

        return await self.handle_request(
            await self._session.put(
                url=self.get_escaped_datapoints_url(self.path(path)),
                data='{"Value": "' + str(body) + '"}',
                headers=self.get_headers_with_token(self.token),
            )
        )

    async def post(self, path: str, data: str) -> Any:
        """Post request."""

        LOGGER.debug("post=%s", path)

        return await self.handle_request(
            await self._session.post(
                url=path,
                headers=self.get_headers(),
                data=data,
            )
        )

    async def auth(self) -> bool:
        """Set token."""

        if self.token_refreshdate == date.today():
            self.token = FlexitToken.from_dict(
                await self.post(
                    path=TOKEN_PATH,
                    data=f"grant_type=password&username={self._username}&password={self._password}",
                )
            ).access_token
            self.token_refreshdate = date.today() + timedelta(days=1)

        return True

    async def find_plants(self) -> List[FlexitPlantItem]:
        """Find plants."""

        await self.auth()
        return FlexitPlants.from_dict(await self.get_url(PLANTS_PATH)).items

    def create_list_from_paths(self, paths: List[str]) -> str:
        """Create path from PATH_LIST."""

        path_str: str = "["

        for path in paths:
            path_str += f"""{{"DataPoints":"{self.path(path)}"}}"""
            path_str += "," if path != paths[-1] else "]"

        return path_str

    async def sensor_data(self) -> FlexitSensorsResponse:
        """Fetch data."""

        await self.auth()
        assert self._plant_id is not None

        return FlexitSensorsResponse.from_dict(
            self._plant_id,
            await self.get(self.create_list_from_paths(SENSOR_DATA_PATH_LIST)),
        )

    async def device_info(self) -> FlexitDeviceInfo:
        """Fetch device info."""

        await self.auth()
        assert self._plant_id is not None

        return FlexitDeviceInfo.from_dict(
            self._plant_id,
            await self.get(self.create_list_from_paths(DEVICE_INFO_PATH_LIST)),
        )

    async def set_home_temp(self, temp) -> bool:
        """Set home temp."""

        return self.is_success(
            await self.put(HOME_AIR_TEMPERATURE_PATH, temp),
            self.path(HOME_AIR_TEMPERATURE_PATH),
        )

    async def set_away_temp(self, temp) -> bool:
        """Set away temp."""

        return self.is_success(
            await self.put(AWAY_AIR_TEMPERATURE_PATH, temp),
            self.path(AWAY_AIR_TEMPERATURE_PATH),
        )

    async def set_mode(self, mode: str) -> bool:
        """Set ventilation mode."""

        mode_int = {
            MODE_HOME: 0,
            MODE_AWAY: 2,
            MODE_HIGH: 4,
        }.get(mode, -1)

        if mode_int == -1:
            return False

        return self.is_success(
            await self.put(VENTILATION_MODE_PUT_PATH, mode_int),
            self.path(VENTILATION_MODE_PUT_PATH),
        )

    async def set_heater_state(self, heater_bool: bool) -> bool:
        """Set heater state."""

        return self.is_success(
            await self.put(ELECTRIC_HEATER_PATH, 1 if heater_bool else 0),
            self.path(ELECTRIC_HEATER_PATH),
        )

    def get_headers(self) -> Dict[str, str]:
        """Get generic headers."""

        return {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-us",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "Flexit%20GO/2.0.6 CFNetwork/1128.0.1 Darwin/19.6.0",
            "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        }

    def get_headers_with_token(self, token: Optional[str]) -> Dict[str, str]:
        """Get headers with token added."""

        assert token is not None
        headers = self.get_headers()
        headers["Authorization"] = f"Bearer {token}"
        return headers

    def is_success(self, response: Dict[str, Any], path_with_plant: str) -> bool:
        """Check if response is successful."""

        stateTexts = FlexitSensorsResponseStatus.from_dict(response).stateTexts

        return stateTexts[path_with_plant] == RESULT_SUCCESS

    def get_escaped_datapoints_url(self, id: str) -> str:
        """Util for adding DATAPOINTS_PATH."""

        return f"{DATAPOINTS_PATH}/{urllib.parse.quote(id)}"

    def get_escaped_filter_url(self, path: str) -> str:
        """Util for adding FILTER_PATH."""

        return f"{FILTER_PATH}{urllib.parse.quote(path)}"
