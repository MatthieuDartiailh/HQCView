# -*- coding: utf-8 -*-
# =============================================================================
# module :  hqc_view/storing/leaves/table_leaf.py
# author : Matthieu Dartiailh
# license : MIT license
# =============================================================================
"""
"""
from atom.api import Property, Typed, set_default
from pandas import DataFrame
from .base_leaf import BaseLeaf


class TableLeaf(BaseLeaf):
    """ Leaf storing data which are stored as named columns.

    """
    # --- Public API ----------------------------------------------------------

    #: Property giving to the columns names of the data.
    names = Property()

    contexts = set_default('release', 'names', 'data', 'c_update')


    def __getitem__(self, key):
        """ Access a column of the data by name.

        This a convenience method, equivalent to leaf.data[key]

        Parameters
        ----------
        key : str
            Name of the column to retrieve from the table.

        Returns
        -------
        column : Series
            Data stored in the specified column of the table.

        """
        return self._data[key]

    def __setitem__(self, key, val):
        """ Set the value of a given column.

        This should be the preferred method to change the value of a column
        as it will call the observers linked to the c_update context.

        Parameters
        ----------
        key : str
            Name of the column whose values should be set.

        val : array-like
            New values of the column.

        """
        old = self._data[key]
        change = {'name': key, 'value': val, 'oldvalue': old}
        self._data[key] = val
        self.call_observers('c_update', change)

    def __delitem__(self, key):
        """ Remove the specified column from the table.

        Parameters
        ----------
        key : str
            Name of the column to remove.

        """
        old = self._data[key]
        change = {'name': key, 'value': [], 'oldvalue': old}
        del self._data[key]
        self.call_observers('c_update', change)

    def rename(self, key, new_key):
        """ Rename the specified column.

        Parameters
        ----------
        key : str
            Name of the column to rename.

        new_key : str
            New name of the column.

        """
        old_names = self._data.columns
        self._data.rename(columns={key: new_key}, inplace=True)
        change = {'value': self._data.columns, 'oldvalue': old_names}
        self.call_observers('names', change)

    def move(self, key, index):
        """ Move the given column to a new position.

        Parameters
        ----------
        key : str
            Name of the column to move.

        index : str
            Index at which the column should be inserted.

        """
        columns  = self._data.columns
        old_columns = columns[:]
        del columns[columns.index(key)]
        columns.insert[key, index]
        self._data.reindex_axis(columns, axis=1)
        change = {'value': columns, 'oldvalue': old_columns}
        self.call_observers('names', change)

    def append(self, key, data):
        """
        """
        pass

    def delete(self, key):
        """
        """
        pass

    def append_rows(self, rows):
        """
        """
        pass


    # --- Private API ---------------------------------------------------------

    #: Reference to the DataFrame used to store the datas.
    _data = Typed(DataFrame)

    def _get_names(self):
        """ Property getter for the names member.

        """
        return self._data.columns
