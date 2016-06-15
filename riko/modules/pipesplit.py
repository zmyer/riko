# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
"""
riko.modules.pipesplit
~~~~~~~~~~~~~~~~~~~~~~
Provides functions for splitting a stream into identical copies

Use split when you want to perform different operations on data from the same
stream. The Union module is the reverse of Split, it merges multiple input
streams into a single combined stream.

Examples:
    basic usage::

        >>> from riko.modules.pipesplit import pipe
        >>> stream1, stream2 = pipe({'x': x} for x in range(5))
        >>> next(stream1)
        {u'x': 0}

Attributes:
    OPTS (dict): The default pipe options
    DEFAULTS (dict): The default parser options
"""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)


from copy import deepcopy

from builtins import *

from . import operator
from riko.lib.log import Logger

OPTS = {'extract': 'splits', 'ptype': 'int', 'objectify': False}
DEFAULTS = {'splits': 2}
logger = Logger(__name__).logger


def parser(stream, splits, tuples, **kwargs):
    """ Parses the pipe content

    Args:
        stream (Iter[dict]): The source stream. Note: this shares the `tuples`
            iterator, so consuming it will consume `tuples` as well.

        splits (int): the number of copies to create.

        tuples (Iter[(dict, obj)]): Iterable of tuples of (item, splits)
            `item` is an element in the source stream (a DotDict instance)
            and `splits` is an int. Note: this shares the `stream` iterator,
            so consuming it will consume `stream` as well.

        kwargs (dict): Keyword arguments.

    Yields:
        Iter(dict): a stream of items

    Examples:
        >>> from itertools import repeat
        >>>
        >>> conf = {'splits': 3}
        >>> kwargs = {'conf': conf}
        >>> stream = (({'x': x}) for x in range(5))
        >>> tuples = zip(stream, repeat(conf['splits']))
        >>> streams = parser(stream, conf['splits'], tuples, **kwargs)
        >>> next(next(streams))
        {u'x': 0}
    """
    source = list(stream)

    # deepcopy each item so that each split is independent
    for num in range(splits):
        yield map(deepcopy, source)


@operator(DEFAULTS, async=True, **OPTS)
def asyncPipe(*args, **kwargs):
    """An operator that asynchronously and eagerly splits a stream into identical
    copies. Note that this pipe is not lazy.

    Args:
        items (Iter[dict]): The source stream.
        kwargs (dict): The keyword arguments passed to the wrapper

    Kwargs:
        conf (dict): The pipe configuration. May contain the key 'splits'.

            splits (int): the number of copies to create (default: 2).

    Returns:
        Deferred: twisted.internet.defer.Deferred iterable of streams

    Examples:
        >>> from twisted.internet.task import react
        >>> from riko.twisted import utils as tu
        >>>
        >>> def run(reactor):
        ...     callback = lambda x: print(next(next(x)))
        ...     d = asyncPipe({'x': x} for x in range(5))
        ...     return d.addCallbacks(callback, logger.error)
        >>>
        >>> try:
        ...     react(run, _reactor=tu.FakeReactor())
        ... except SystemExit:
        ...     pass
        ...
        {u'x': 0}
    """
    return parser(*args, **kwargs)


@operator(DEFAULTS, **OPTS)
def pipe(*args, **kwargs):
    """An operator that eagerly splits a stream into identical copies.
    Note that this pipe is not lazy.

    Args:
        items (Iter[dict]): The source stream.
        kwargs (dict): The keyword arguments passed to the wrapper

    Kwargs:
        conf (dict): The pipe configuration. May contain the key 'splits'.

            splits (int): the number of copies to create (default: 2).

    Yields:
        Iter(dict): a stream of items

    Examples:
        >>> items = [{'x': x} for x in range(5)]
        >>> stream1, stream2 = pipe(items)
        >>> next(stream1)
        {u'x': 0}
        >>> len(list(pipe(items, conf={'splits': '3'})))
        3
    """
    return parser(*args, **kwargs)
