# -*- coding: utf-8 -*-
# =============================================================================
# module :  hqc_view/storing/leaves/matrix_leaf.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import Property, Typed, set_default
from pandas import DataFrame
from .base_leaf import BaseLeaf


class MatrixLeaf(BaseLeaf):
    """ Leaf storing data which are stored as named columns.

    """
    # --- Public API ----------------------------------------------------------

    shape = Property()

    data = Property()

    contexts = set_default('release', 'shape', 'data')


    def update_data(self, new_data):
        """
        """
        pass


    # --- Private API ---------------------------------------------------------

    #: Reference to the DataFrame used to store the datas.
    _data = Typed(DataFrame)

    def _get_shape(self):
        """
        """
        pass

    def _get_data(self):
        """
        """
        pass
