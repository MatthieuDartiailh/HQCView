# -*- coding: utf-8 -*-
# =============================================================================
# module :  hqc_view/storing/leaves/base_leaf.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import Property, Typed, set_default
from pandas import DataFrame
from ..base_node import BaseNode


class BaseLeaf(BaseNode):
    """ Base leaf used to store data.

    """
    # --- Public API ----------------------------------------------------------

    #: Property giving access to the data stored into the leaf.
    data = Property()

    contexts = set_default('release', 'data')

    def release_data(self):
        """ Delete the data and notifies the observer they should do the same.

        """
        self.call_observers('release', {})
        del self._data


    # --- Private API ---------------------------------------------------------

    #: Reference to the DataFrame used to store the datas.
    _data = Typed(DataFrame)


    def _get_data(self):
        """ Getter for the data member.

        """
        return self._data

    def _set_data(self, data):
        """ Setter for the data member.

        Setting the data will fire the observers of the 'data' context.

        """
        old = self._data
        change = {'value': data, 'oldvalue': old}
        self._data = data
        self.call_observers('data', change)
