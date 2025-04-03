from .JMS import JMS

from importlib import metadata

try:
    __version__ = metadata.version("robotframework-jmslibrary")
except metadata.PackageNotFoundError:
    pass