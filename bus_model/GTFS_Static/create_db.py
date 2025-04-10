"""
Create the databases from txt files and filter them to include only cork city routes
"""

from .db_connection import close_connection, create_connection
from .create_tables import TableCreator
from .populate_tables import TablePopulator
from .index_tables import TableIndexer
from .filter_tables import TableFilter

if __name__ == "__main__":
    conn = create_connection()
    conn.autocommit = True
    tc = TableCreator(conn)
    tp = TablePopulator(conn)
    ti = TableIndexer(conn)
    tf = TableFilter(conn)
    tc.create_tables()
    tp.populate_tables()
    ti.create_indexes_before_filter()
    tf.filter_tables()
    ti.create_indexes_after_filter()
    close_connection(conn)
