"""
🔐 Admin Routes - Secret control panel
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from app.admin.system_controller import system_controller

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


class SystemToggleResponse(BaseModel):
    enabled: bool
    status: str
    message: str


@router.get("/status")
async def get_system_status():
    """Get current system status"""
    return system_controller.get_status()


@router.post("/toggle")
async def toggle_system():
    """Toggle system on/off"""
    logger.warning("🎛️ Admin toggle requested")
    enabled = system_controller.toggle()
    status = system_controller.get_status()
    
    return {
        **status,
        "action": "enabled" if enabled else "disabled"
    }


@router.post("/enable")
async def enable_system():
    """Enable system"""
    logger.warning("🟢 Admin enable requested")
    system_controller.enable()
    return system_controller.get_status()


@router.post("/disable")
async def disable_system():
    """Disable system"""
    logger.warning("🔴 Admin disable requested")
    system_controller.disable()
    return system_controller.get_status()

