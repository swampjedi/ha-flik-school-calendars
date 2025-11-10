"""Nutrislice API types."""

from typing import TypedDict


class OrgSettings(TypedDict):
    """Organization Settings."""

    org_id: str
    district_name: str
    address1: str
    address2: str
    city: str
    state: str
    zip: str
    contact_email: str
    director_name: str


class SchoolMenu(TypedDict):
    """Top-level Menu."""

    id: int
    name: str
    slug: str


class School(TypedDict):
    """A School within an Organization."""

    id: int
    name: str
    slug: str
    menus: list[SchoolMenu]


class MenuFood(TypedDict):
    """Food Item on a Menu."""

    id: str
    name: str
    description: str
    category: str


class MenuSection(TypedDict):
    """Subsection of a Menu."""

    id: str
    text: str
    food: list[MenuFood]


class MenuDay(TypedDict):
    """A Menu for a specific Day."""

    date: str
    sections: list[MenuSection]
