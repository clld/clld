from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol

from {{cookiecutter.directory_name}} import models


def includeme(config):
    """register custom datatables"""
