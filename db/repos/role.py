from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class RoleRepository(ABC):
    @abstractmethod
    async def list_roles(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def list_actions(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def create_role(self, name: str, description: str | None, action_names: list[str]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def update_role(
        self,
        role_id: UUID,
        name: str,
        description: str | None,
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    async def add_actions_to_role(
        self,
        role_id: UUID,
        action_names: list[str],
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    async def remove_action_from_role(
        self,
        role_id: UUID,
        action_name: str,
    ) -> dict[str, Any]:
        ...
