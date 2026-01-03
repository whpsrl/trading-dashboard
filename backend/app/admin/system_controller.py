"""
🔴🟢 System Controller - Master Kill Switch
Controls all auto-scan, trade tracker, and news systems
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemController:
    """Global system state controller"""
    
    def __init__(self):
        self.state_file = Path("system_state.txt")
        self._load_state()
        logger.info(f"🎛️ System Controller initialized (System: {'ON ✅' if self.is_enabled else 'OFF 🔴'})")
    
    def _load_state(self):
        """Load system state from file"""
        try:
            if self.state_file.exists():
                state = self.state_file.read_text().strip()
                self.is_enabled = (state == "ON")
                logger.info(f"📂 Loaded system state from file: {state}")
            else:
                # Default: system ON
                self.is_enabled = True
                self._save_state()
                logger.info("📂 No state file found, defaulting to ON")
        except Exception as e:
            logger.error(f"❌ Error loading system state: {e}")
            self.is_enabled = True
    
    def _save_state(self):
        """Save system state to file"""
        try:
            state = "ON" if self.is_enabled else "OFF"
            self.state_file.write_text(state)
            logger.info(f"💾 Saved system state: {state}")
        except Exception as e:
            logger.error(f"❌ Error saving system state: {e}")
    
    def enable(self):
        """Enable all systems"""
        if not self.is_enabled:
            self.is_enabled = True
            self._save_state()
            logger.warning("🟢 SYSTEM ENABLED - All auto-scans, trade tracker, and news will run")
        return self.is_enabled
    
    def disable(self):
        """Disable all systems"""
        if self.is_enabled:
            self.is_enabled = False
            self._save_state()
            logger.warning("🔴 SYSTEM DISABLED - All auto-scans, trade tracker, and news are STOPPED")
        return self.is_enabled
    
    def toggle(self):
        """Toggle system state"""
        if self.is_enabled:
            return self.disable()
        else:
            return self.enable()
    
    def get_status(self):
        """Get current system status"""
        return {
            "enabled": self.is_enabled,
            "status": "online" if self.is_enabled else "offline",
            "message": "System is running normally" if self.is_enabled else "System is DISABLED - No auto-scans running"
        }


# Global singleton instance
system_controller = SystemController()

