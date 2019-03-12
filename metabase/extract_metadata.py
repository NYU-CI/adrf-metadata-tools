"""Class to extract metadata from a Data Table"""

import getpass
import psycopg2
from psycopg2 import sql

# TODO: move away from sqlalchemy
import sqlalchemy

from . import settings


class ExtractMetadata():
    """Class to extract metadata from a Data Table."""

    def __init__(self, data_table_id):
        """Set Data Table ID and connect to database.

        Args:
           data_table_id (int): ID associated with this Data Table.

        """
        self.data_table_id = data_table_id

        self.metabase_conn = psycopg2.connect(settings.metabase_connection_string)
        self.metabase_conn.autocommit = True
        self.metabase_cur = self.metabase_conn.cursor()

        self.data_conn = psycopg2.connect(settings.data_connection_string)
        self.data_conn.autocommit = True
        self.data_cur = self.data_conn.cursor()

        self.schema_name, self.table_name = self.__get_table_name()

    def process_table(self, categorical_threshold=10):
        """Update the metabase with metadata from this Data Table."""

        self._get_table_level_metadata()
        self._get_column_level_metadata(categorical_threshold)

        self.metabase_cur.close()
        self.metabase_conn.close()
        self.data_cur.close()
        self.data_conn.close()

    def _get_table_level_metadata(self):
        """Extract table level metadata and store it in the metabase.

        Extract table level metadata (number of rows, number of columns and
        file size (table size)) and store it in DataTable. Also set updated by
        and date last updated.

        Size is in bytes

        """
        self.data_cur.execute(
            sql.SQL('SELECT COUNT(*) as n_rows FROM {}.{};').format(
                sql.Identifier(self.schema_name),
                sql.Identifier(self.table_name),
            )
        )
        n_rows = self.data_cur.fetchone()[0]

        self.data_cur.execute(
            sql.SQL("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE
                    TABLE_SCHEMA = %s
                    AND TABLE_NAME = %s
            """),
            [self.schema_name, self.table_name]
        )
        n_cols = self.data_cur.fetchone()[0]

        self.data_cur.execute(
            sql.SQL('SELECT PG_RELATION_SIZE(%s);'),
            [self.schema_name + '.' + self.table_name],
        )
        table_size = self.data_cur.fetchone()[0]

        if n_rows == 0:
            raise ValueError('Selected data table has 0 rows.')
        elif n_cols == 0:
            raise ValueError('Selected data table has 0 columns.')
        elif table_size == 0:
            raise ValueError('The size of the selected data table is 0 byte.')

        self.metabase_cur.execute(
            """
                UPDATE metabase.data_table
                SET
                    number_rows = %(n_rows)s,
                    number_columns = %(n_cols)s,
                    size = %(table_size)s,
                    updated_by = %(user_name)s,
                    date_last_updated = (SELECT CURRENT_TIMESTAMP)
                WHERE data_table_id = %(data_table_id)s
                ;
            """,
            {
                'n_rows': n_rows,
                'n_cols': n_cols,
                'table_size': table_size,
                'user_name': getpass.getuser(),
                'data_table_id': self.data_table_id,
            }
        )

    def _get_column_level_metadata(self, categorical_threshold):
        """Extract column level metadata and store it in the metabase.

        Process columns one by one, identify or infer type, update Column Info
        and corresponding column table.

        """

        column_type = self.__get_column_type(categorical_threshold)
        if column_type == 'numeric':
            self.get_numeric_metadata()
        elif column_type == 'text':
            self.get_text_metadata()
        elif column_type == 'date':
            self.get_date_metadate()
        elif column_type == 'code':
            self.get_code_metadata()
        else:
            raise ValueError('Unknow column type')

    def __get_table_name(self):
        """Return the the table schema and name using the Data Table ID.

        Returns table name and schema name by looking up the Data Table ID in
        the metabase. The table name and schema name will be used to query the
        table itself.

        Returns:
            (str, str): (schema name, table name)

        """
        self.metabase_cur.execute(
            """
            SELECT file_table_name
            FROM metabase.data_table
            WHERE data_table_id = %(data_table_id)s;
            """,
            {'data_table_id': self.data_table_id},
        )

        try:
            schema_name, table_name = self.metabase_cur.fetchone(
                )[0].split('.')
        except TypeError:
            raise ValueError('data_table_id not found in DataTable')

        return schema_name, table_name

    def __get_column_type(self, categorical_threshold):
        """Identify or infer column type.

        Uses the type set in the database if avaible. If all columns are text,
        attempts to infer the column type.

        Returns:
          str: 'numeric', 'text', 'date' or 'code'

        """

        # TODO
        pass

    def __get_numeric_metadata(self):
        """Extract metadata from a numeric column.

        Extract metadata from a numeric column and store metadata in Column
        Info and Numeric Column. Update relevant audit fields.

        """

        # TODO
        pass

    def __get_text_metadata(self):
        """Extract metadata from a text column.

        Extract metadata from a text column and store metadata in Column Info
        and Text Column. Update relevant audit fields.

        """

        # TODO
        pass

    def __get_date_metadata(self):
        """Extract metadata from a date column.

        Extract metadata from date column and store metadate in Column Info and
        Date Column. Update relevant audit fields.

        """

        # TODO
        pass

    def __get_code_metadata(self):
        """Extract metadata from a categorial column.

        Extract metadata from a categorial columns and store metadata in Column
        Info and Code Frequency. Update relevant audit fields.

        """

        # TODO
        pass
