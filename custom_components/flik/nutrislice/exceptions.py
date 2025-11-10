"""Exceptions."""


class InvalidOrganiztion(Exception):
    """Raised when an invalid organization is used."""

    def __init__(self, organization) -> None:
        """Set Organization."""
        self.organization = organization

    def __str__(self) -> str:
        """To String."""
        return f"Invalid organization: {self.organization}"
