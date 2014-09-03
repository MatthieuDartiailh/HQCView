# -*- coding: utf-8 -*-
# =============================================================================
# module :  hqc_view/storing/base_node.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
import logging
from atom.api import Atom, List, Typed, Unicode, Bool
from weakref import WeakSet
from collection import defaultdict
from contextlib import contextmanager


class BaseNode(Atom):
    """ Base class for database node and leafs, handling the use of observers.

    Those observers are custom observers that I found no way to reduce to
    standard Atom observer. They are attached to a context described by a
    string and called at appropriate times. The callbacks are passed a dict
    similar to what Atom would send.

    """
    # --- Public API ----------------------------------------------------------

    #: Name of the node.
    name = Unicode()

    #: Path of the node in the database.
    path = Unicode()

    #:  The list of valid contexts this object declare.
    contexts = List()

    def attach_observer(self, context, callback):
        """
        """
        pass

    def detach_observer(self, context, callback):
        """
        """
        pass

    def detach_observers(self, context=None):
        """
        """
        pass

    @contextmanager
    def suspend_observers(self):
        """
        """
        yield

    def call_observers(self, context, change):
        """
        """
        pass

    # --- Private API ---------------------------------------------------------

    #: Dict storing the observers for each context in WeakSet (not memory
    #: optimal but no choice as I cannot simply use Atom observers).
    _callbacks = Typed(defaultdict(WeakSet))

    #: Flag used to suspend the notifications.
    _no_notif = Bool()
