from typing import List
from uuid import UUID
from pydantic import BaseModel


class UserPermissions(BaseModel):
  ResourceType: str
  ResourceId: str
  Permissions: List[str] = []


class RoleCreateRequest(BaseModel):
    name: str
    description: str | None = None
    actions: List[str] = []


class RoleUpdateRequest(BaseModel):
    name: str
    description: str | None = None


class RoleActionsRequest(BaseModel):
    names: List[str]


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    actions: List[str] = []


class ActionResponse(BaseModel):
    name: str
    description: str | None = None
    is_global: bool | None = None

