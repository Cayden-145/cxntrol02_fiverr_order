class MissingAdminRole(Exception):
    """Exception raised when a user does not have admin privileges."""
    pass

class MissingGuildOwner(Exception):
    """Exception raised when a user is not the guild owner."""
    pass

class MissingStaffRole(Exception):
    """Exception raised when a user does not have the required staff role."""
    pass

class MissingPermission(Exception):
    """Exception raised when a user does not have the required permissions to run a moderation command."""
    pass