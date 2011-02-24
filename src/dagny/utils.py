# -*- coding: utf-8 -*-

import re


def camel_to_underscore(camel_string):

    """
    Convert a CamelCase string to under_score.

    Examples:

        >>> camel_to_underscore('SplitAtTheBoundaries')
        'split_at_the_boundaries'

        >>> camel_to_underscore('XYZResource')
        'xyz_resource'

        >>> camel_to_underscore('ResourceXYZ')
        'resource_xyz'

        >>> camel_to_underscore('XYZ')
        'xyz'

    """

    return re.sub(
        r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', r'_\1',
        camel_string).lower().strip('_')


def resource_name(resource_cls):
    """Return the name of a given resource, stripping 'Resource' off the end."""

    from dagny import Resource

    if isinstance(resource_cls, Resource):
        resource_cls = resource_cls.__class__

    name = resource_cls.__name__
    if name.endswith('Resource'):
        return name[:-8]
    return name
