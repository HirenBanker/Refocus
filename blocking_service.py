import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BlockingService:
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self._is_active = False
        self._block_until = None
        self._blocked_sites = []
        
        # Sync with persisted state
        if self.data_manager:
            state = self.data_manager.get_blocking_state()
            if state.get("blocking_active"):
                until_str = state.get("block_until")
                if until_str:
                    try:
                        self._block_until = datetime.fromisoformat(until_str)
                        if datetime.now() > self._block_until:
                            self.stop_blocking(force=True)
                        else:
                            self._is_active = True
                            self._blocked_sites = self.data_manager.get_blocked_sites()
                    except ValueError:
                        self.stop_blocking(force=True)

    def start_blocking(self, duration_minutes, sites, strict=True):
        """
        Starts the blocking session.
        :param duration_minutes: Duration in minutes
        :param sites: List of sites to block
        :param strict: If True, blocking cannot be stopped early
        """
        self._block_until = datetime.now() + timedelta(minutes=duration_minutes)
        self._blocked_sites = sites
        self._is_active = True
        
        if self.data_manager:
            self.data_manager.update_blocking_state(
                active=True,
                until=self._block_until.isoformat(),
                strict=strict
            )

        logging.info(f"Blocking started for {duration_minutes} minutes. Strict: {strict}")
        logging.info(f"Sites blocked: {', '.join(sites)}")
        
        self._enforce_blocking()

    def stop_blocking(self, force=False):
        """
        Stops the blocking session.
        :param force: If True, bypasses strict check (for internal use/expiration)
        :return: True if stopped, False if denied by strict mode
        """
        if not force and self.data_manager:
            state = self.data_manager.get_blocking_state()
            strict = state.get("strict_mode", True)
            until_str = state.get("block_until")
            if strict and until_str:
                try:
                    until = datetime.fromisoformat(until_str)
                    if datetime.now() < until:
                        logging.warning("Attempt to stop strict blocking denied.")
                        return False # Cannot stop
                except ValueError:
                    pass

        self._is_active = False
        self._block_until = None
        self._blocked_sites = []
        
        if self.data_manager:
            self.data_manager.update_blocking_state(active=False, until=None, strict=True)
        
        logging.info("Blocking stopped.")
        self._lift_blocking()
        return True

    def is_active(self):
        """
        Checks if blocking is currently active.
        """
        if self.data_manager:
            state = self.data_manager.get_blocking_state()
            if not state.get("blocking_active"):
                return False
            
            until_str = state.get("block_until")
            if until_str:
                try:
                    until = datetime.fromisoformat(until_str)
                    if datetime.now() > until:
                        self.stop_blocking(force=True)
                        return False
                    return True
                except ValueError:
                    self.stop_blocking(force=True)
                    return False
        
        # Fallback for when data_manager is not present (e.g. basic tests)
        if self._is_active and self._block_until:
            if datetime.now() > self._block_until:
                self.stop_blocking(force=True)
                return False
            return True
            
        return False

    def get_remaining_time(self):
        if self.is_active() and self._block_until:
            remaining = self._block_until - datetime.now()
            return max(timedelta(0), remaining)
        return timedelta(0)

    def get_block_until(self):
        if self.is_active():
            return self._block_until
        return None

    def _enforce_blocking(self):
        # Placeholder for actual blocking logic
        pass

    def _lift_blocking(self):
        # Placeholder for actual unblocking logic
        pass
