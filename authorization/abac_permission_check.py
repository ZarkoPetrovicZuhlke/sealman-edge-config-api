from fastapi import Depends, Request
import logging

from auth import get_current_user, validate_jwt


logger = logging.getLogger("EdgeConfigAPI")


class ABACPermissionCheck:
    def __init__(self, permission: str, device_path: str = "device"):
        self.permission = permission
        self.device_path = device_path

    async def __call__(self, request: Request, auth_context: dict = Depends(validate_jwt)) -> dict:
        device_id = request.path_params.get(self.device_path) if self.device_path else None
        # permission check logic goes here
        logger.info(f"ABAC permission check: {self.permission} for device {device_id} by user {get_current_user(auth_context)}")

        return {
            "user_name": get_current_user(auth_context),
            "user_id": auth_context.get("oid") or auth_context.get("sub"),
            "permission": self.permission,
            "device_id": device_id
        }
