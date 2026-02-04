"""API module for Cocoa Price Tracker."""

from .routes import router
from .dashboard import dashboard_router

__all__ = ["router", "dashboard_router"]
