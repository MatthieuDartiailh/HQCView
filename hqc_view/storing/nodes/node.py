# -*- coding: utf-8 -*-
# =============================================================================
# module :  hqc_view/storing/nodes/node.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import Dict, Unicode, Typed, set_default
from ..base_node import BaseNode


class Node(BaseNode):
    """ Base kind of node for the database.

    """   
    # --- Public API ----------------------------------------------------------
    
    contexts = set_default('children')
    
    def __setitem__(self, key, obj):
        """
        """
        pass
        
    def __getitem__(self, key):
        """
        """
        pass
    
    def __delitem__(self, key):
        """
        """
        pass
    

    # --- Private API ---------------------------------------------------------

    #: Dict of children attached to this node. This dict should not be 
    #: manipulated by user code.
    _children = Dict(Unicode(), Typed(BaseNode))
    