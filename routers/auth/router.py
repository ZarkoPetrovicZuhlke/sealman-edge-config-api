from fastapi import Depends, HTTPException
from uuid import UUID
from auth import RBACPermissionChecker, validate_jwt
from authorization.permission_types import Device, Platform
from exceptions import UserNotFound
from db.repos.role import RoleRepository
from db.session import get_repository
from routers.auth.routes.delete_role_action_by_name import delete_role_action_by_name as _delete_role_action_by_name
from routers.auth.routes.get_actions import get_actions as _get_actions
from routers.auth.routes.get_roles import get_roles as _get_roles
from routers.auth.routes.post_role import post_role as _post_role
from routers.auth.routes.post_role_actions import post_role_actions as _post_role_actions
from routers.auth.routes.put_role_by_id import put_role_by_id as _put_role_by_id
from routers.auth.schemas import (
    ActionResponse,
    RoleActionsRequest,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
    UserPermissions,
)
from routers.base_api_router import BaseAPIRouter
from constants import AUTHORIZATION_API_PLATFORM_NAME


auth = BaseAPIRouter()


@auth.get("/auth/roles", response_model=list[RoleResponse], tags=["Auth"])
async def get_roles(role_repo: RoleRepository = Depends(get_repository(RoleRepository))):
    return await _get_roles(role_repo)


@auth.get("/auth/actions", response_model=list[ActionResponse], tags=["Auth"])
async def get_actions(role_repo: RoleRepository = Depends(get_repository(RoleRepository))):
    return await _get_actions(role_repo)


@auth.post("/auth/roles", response_model=RoleResponse, tags=["Auth"])
async def post_role(
    body: RoleCreateRequest,
    role_repo: RoleRepository = Depends(get_repository(RoleRepository)),
):
    return await _post_role(body, role_repo)


@auth.put("/auth/roles/{role_id}", response_model=RoleResponse, tags=["Auth"])
async def put_role_by_id(
    role_id: UUID,
    body: RoleUpdateRequest,
    role_repo: RoleRepository = Depends(get_repository(RoleRepository)),
):
    return await _put_role_by_id(role_id, body, role_repo)


@auth.post("/auth/roles/{role_id}/actions", response_model=RoleResponse, tags=["Auth"])
async def post_role_actions(
    role_id: UUID,
    body: RoleActionsRequest,
    role_repo: RoleRepository = Depends(get_repository(RoleRepository)),
):
    return await _post_role_actions(role_id, body, role_repo)


@auth.delete(
    "/auth/roles/{role_id}/actions/{name}",
    response_model=RoleResponse,
    tags=["Auth"],
)
async def delete_role_action_by_name(
    role_id: UUID,
    name: str,
    role_repo: RoleRepository = Depends(get_repository(RoleRepository)),
):
    return await _delete_role_action_by_name(role_id, name, role_repo)


@auth.get(
    "/auth/permissions/{resource_type}", response_model=UserPermissions, tags=["Auth"]
)
async def get_permissions(
    resource_type: str,
    resource_id: str = None,
    auth_context: dict = Depends(validate_jwt),
):

    if resource_type == "platform" and resource_id is None:
        resource_id = AUTHORIZATION_API_PLATFORM_NAME

    if resource_id is None:
        raise HTTPException(status_code=400, detail="resource_id is required")

    user_id = auth_context.get("oid") or auth_context.get("sub")
    if (user_id is None):
        raise UserNotFound(status_code=403)

    # In RBAC mode, derive permissions from the user's assigned roles.
    if resource_type.lower() == "platform":
        permission_resource_type = Platform
    elif resource_type.lower() == "device":
        permission_resource_type = Device
    else:
        raise HTTPException(status_code=400, detail="Invalid resource type")

    assigned_permissions = RBACPermissionChecker.get_assigned_permissions(auth_context)
    assigned_permission_map = {perm: True for perm in assigned_permissions}
    available_permissions = {
        value
        for attr in dir(permission_resource_type)
        if not attr.startswith("__")
        for value in [getattr(permission_resource_type, attr)]
        if isinstance(value, str)
    }
    user_permissions = [
        permission for permission in available_permissions if permission in assigned_permission_map
    ]

    return UserPermissions(
        ResourceType=resource_type, ResourceId=resource_id, Permissions=user_permissions
    )