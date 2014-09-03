# -*- coding: utf-8 -*-
# =============================================================================
# module :  hqc_view/storing/storing_database.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import Atom, Typed

from .nodes.node import Node

class StoringDatabase(Atom):
    """
    """
    # --- Public API ----------------------------------------------------------
    
    def get_node(self, path):
        """
        """
        pass
    
    def create_node(self, path, factory=Node):
        """
        """
        pass
    
    def delete_node(self, path):
        """
        """
        pass
    
    # --- Private API ---------------------------------------------------------
    
    #: Reference to the root Node which is not supposed to be accessed directly
    _root = Typed(Node)
    