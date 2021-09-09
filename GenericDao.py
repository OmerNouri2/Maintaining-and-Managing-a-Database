import inspect


class GenericDao:
    def __init__(self, dto_type, conn):
        self._conn = conn
        self._dto_type = dto_type

        # dto_type is a class, its __name__ field contains a string representing the name of the class.
        self._table_name = dto_type.__name__.lower() + 's'

    def insert(self, dto_instance):
        insert_dict_to_db = vars(dto_instance)

        # parameters required for the insertion query
        column_names = ','.join(insert_dict_to_db.keys())
        params = list(insert_dict_to_db.values())
        # params = [1,"1-12-2012",1,3]
        qmarks = ','.join(['?'] * len(insert_dict_to_db))

        q_insertion = 'INSERT INTO {} ({}) VALUES ({})'.format(self._table_name, column_names, qmarks)

        # add to the table the dto_instance
        self._conn.execute(q_insertion, params)

    def row_map(self, row, col_mapping, dto_type):
        ctor_args = [row[idx] for idx in col_mapping]
        return dto_type(*ctor_args)

    # The ORM is a method for mapping between a certain DTO object and its related
    # table in a manner that suits any given DTO
    def orm(self, cursor, dto_type):
        # the following line retrieve the argument names of the constructor
        # inspect.getfullargspec(func) --> get the names and default values of a Python function’s parameters
        args = inspect.getargspec(dto_type.__init__).args

        # the first argument of the constructor will be 'self', it does not correspond
        # to any database field, so we can ignore it.
        args = args[1:]

        # gets the names of the columns returned in the cursor
        col_names = [column[0] for column in cursor.description]

        # map them into the position of the corresponding constructor argument
        col_mapping = [col_names.index(arg) for arg in args]
        return [self.row_map(row, col_mapping, dto_type) for row in cursor.fetchall()]

    # find all entries from specific table
    def find_all(self):
        c = self._conn.cursor()
        c.execute('SELECT * FROM {}'.format(self._table_name))
        return self.orm(c, self._dto_type)

    # find specific entry from specific table according to argument - keyvals
    def find(self, **keyvals):
        column_names = keyvals.keys()
        params = list(keyvals.values())

        q_select_where = 'SELECT * FROM {} WHERE {}'.format(self._table_name,
                                                            ' AND '.join([col + '=?' for col in column_names]))

        c = self._conn.cursor()
        c.execute(q_select_where, params)
        return self.orm(c, self._dto_type)

    # delete specific entries from specific table according to argument - keyvals
    def delete(self, **keyvals):
        column_names = keyvals.keys()
        params = list(keyvals.values())

        q_delete_where = 'DELETE FROM {} WHERE {}'.format(self._table_name,
                                                          ' AND '.join([col + '=?' for col in column_names]))

        c = self._conn.cursor()
        c.execute(q_delete_where, params)

    # update specific columns from specific table according to argument - set_values
    def update(self, set_values, cond):
        # the params to update
        set_column_names = set_values.keys()
        set_params = set_values.values()

        # the condition where to update
        cond_column_names = cond.keys()
        cond_params = cond.values()

        params = list(set_params) + list(cond_params)

        q_update_where = 'UPDATE {} SET {} WHERE {}'.format(self._table_name,
                                                            ', '.join([set + '=?' for set in set_column_names]),
                                                            ' AND '.join(
                                                                [cond + '=?' for cond in cond_column_names]))
        self._conn.execute(q_update_where, params)

    def get_supplier_id_with_name(self, name):
        c = self._conn.cursor()
        q_select_where_id = """
            SELECT supplier.id
            FROM suppliers
            WHERE suppliers.name = name
        """
        supplier_id = c.execute(q_select_where_id).fetchone()
        return supplier_id

    def get_logistic_id_by_supplier(self, supplier_id):
        c = self._conn.cursor()
        q_select_where_id = """
            SELECT supplier.logistic
            FROM suppliers
            WHERE suppliers.id = supplier_id
        """
        supplier_logistic = c.execute(q_select_where_id).fetchone()
        return supplier_logistic

    # find specific entry from specific table according to argument - keyvals
    def asc_ordered_by(self, *column):
        column_names = list(column)  # columns to order by

        q_select_where = 'SELECT * FROM {} ORDER BY {}'.format(self._table_name,
                                                               ','.join(['{} ASC'.format(col) for col in column_names]))

        c = self._conn.cursor()
        c.execute(q_select_where)
        return self.orm(c, self._dto_type)
