"""Config flow for Nutrislice Food Calendars integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_CAL_NAME, CONF_ORGANIZATION, CONF_SCHOOL_NAME, DOMAIN
from .nutrislice.api import NutrisliceAPI
from .nutrislice.exceptions import InvalidOrganiztion
from .nutrislice.types import OrgSettings, School

_LOGGER = logging.getLogger(__name__)


class MyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nutrislice Food Calendars."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the Nutrislice flow."""
        self.org_settings: OrgSettings | None = None
        self.schools: list[School] = []
        self.picked_school = None
        self.calname: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        # This is for backwards compatibility.
        return await self.async_step_init(user_input)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - Get the URL of the menu."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                # init api
                # This is the URL input by the user in the setup.
                user_input[CONF_ORGANIZATION] = (
                    user_input[CONF_ORGANIZATION]
                    .replace("http://", "")
                    .replace("https://", "")
                    .strip("/")
                )
                api = NutrisliceAPI(user_input[CONF_ORGANIZATION])
                # get settings
                org_settings = await api.get_settings()
                self.org_settings = org_settings
                # list schools
                schools = await api.list_schools()
                self.schools = schools
                # next step, pick the school
                return await self.async_step_school()
            except InvalidOrganiztion:
                errors["base"] = "invalid_organization"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("organization"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_school(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the school pick step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            self.picked_school = picked_school = next(
                (s for s in self.schools if s["id"] == user_input["school"]), None
            )

            # Don't allow setting up the same school twice
            self._async_abort_entries_match(
                {
                    CONF_ORGANIZATION: self.org_settings["org_id"],
                    CONF_SCHOOL_NAME: self.picked_school["slug"],
                }
            )

            return self.async_show_form(
                step_id="calendarname",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            "calendarname", default=self.picked_school["name"] + " Menu"
                        ): str,
                    }
                ),
                errors=errors,
            )

        # map schools to options
        school_options = {s["id"]: s["name"] for s in self.schools}
        # show form
        return self.async_show_form(
            step_id="school",
            data_schema=vol.Schema(
                {
                    vol.Required("school"): vol.In(school_options),
                }
            ),
            errors=errors,
        )

    async def async_step_calendarname(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(
                title=f"{self.org_settings['org_id']} - {self.picked_school['name']}",
                data={
                    CONF_ORGANIZATION: self.org_settings["org_id"],
                    CONF_SCHOOL_NAME: self.picked_school["slug"],
                    CONF_CAL_NAME: user_input[CONF_CAL_NAME],
                },
            )

        return self.async_show_form(
            step_id="calendarname",
            data_schema=vol.Schema(
                {
                    vol.Required("calendarname"): str,
                }
            ),
            errors=errors,
        )
