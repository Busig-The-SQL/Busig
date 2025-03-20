import pytest








from bus_model.GTFS_Static.db_connection import close_connection, create_connection
from collections import defaultdict

def manage_read_only_connection(func):
    def wrapper(*args, **kwargs):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            return func(cursor, *args, **kwargs)
        finally:
            close_connection(conn)
    return wrapper

# Sample IDs
# trip: 4524_56430
# route: 4497_87348 / 4497_87505 (220X)
# agency: 7778020

class Query:
    """
    Idea: Store sufficient context to allow us to build a full SQL query from a syntax such as trip.route.stop, where all we have to specify is the initial ID
    Context needed:
    - The query so far
        - Depth, variables used
    - table names
    - initial ID
    Precomputation:
    - Find which keys to join on (e.g. connections between route and trip table in either direction need to used route_id key.)
    - Maybe get all headers and overlaps between tables is the key to match on.
    - Have a look-up table which will tell us the key to join on
    - Invalid pairs can also raise impossible actions
    """
    dict_table = {"trip" : "trips", "route" : "routes", "stop" : "stops", "agency" : "agency", "service" : "calendar", "stop_times" : "stop_times"}
    dict_id = {"trip" : "trip_id", "route" : "route_id", "stop" : "stop_id", "agency" : "agency_id", "service" : "service_id"}
    unique_char = 0

    table_headers = defaultdict(list)
    join_keys = defaultdict(dict)
    ___conn = create_connection()
    ___cursor = ___conn.cursor()
    try:
        query = """select table_name, column_name 
        from information_schema.columns 
        where table_name in (
        select tablename from pg_tables where schemaname = 'public');""" 
        ___cursor.execute(query)
        res = ___cursor.fetchall()
        for row in res:
            table_headers[row[0]].append(row[1])
        print(table_headers)
        for header1, fields1 in table_headers.items():
            for header2, fields2 in table_headers.items():
                if header1 != header2:
                    overlap = set(fields1) & set(fields2)
                    if overlap:
                        common_key = list(overlap)[0]
                        join_keys[header1][header2] = common_key
                        join_keys[header2][header1] = common_key
                    else:
                        join_keys[header1][header2] = None
                        join_keys[header2][header1] = None
        print(join_keys)
    finally:
        close_connection(___conn)

    def __init__(self, initial_id, past_tables=None, query="WITH", depth=0):
        self.initial_id = initial_id
        self.query = query
        self.depth = depth
        self.past_tables = past_tables or []


    def __getattr__(self, name):
        print(name)
        table_name = None
        id_name = None
        if name in self.dict_table:
            table_name = self.dict_table[name]
        if name in self.dict_id:
            id_name = self.dict_id[name]
        if table_name:  # match to another table
            if self.depth == 0:
                q = f""" {'_' + str(Query.unique_char)} AS (
                    SELECT * FROM {table_name}
                    WHERE {id_name} = '{self.initial_id}'
                    )"""
            else:
                prev_table = self.past_tables[-1]
                join_key = self.join_keys[prev_table][table_name]
                if join_key:
                    q = f""",
                        {'_' + str(Query.unique_char)} AS (
                        SELECT * FROM {table_name}
                        WHERE {join_key} IN (SELECT {join_key} FROM {'_' + str(Query.unique_char-1)})
                        )"""
                else:
                    raise ValueError(f"Invalid pair of tables: {prev_table} and {table_name}")
        else:
            raise AttributeError(f"Invalid attribute: {name}")
        self.past_tables.append(table_name)
        Query.unique_char += 1
        return Query("", past_tables=self.past_tables, query=self.query + q, depth=self.depth+1)
    
    def __str__(self):
        return self.query
    
    @manage_read_only_connection
    def exec(cursor, self, attribute=""):
        if attribute:
            addition = f"\nSELECT {attribute} FROM {'_' + str(self.depth-1)};"
        else:
            addition = f"\nSELECT * FROM {'_' + str(self.depth-1)};"
        query = self.query + addition
        print(query)
        cursor.execute(query)
        res = cursor.fetchall()
        #print(res)
        return res

    
t = Query("4497_87505").route.trip.stop_times.stop.exec("stop_name")


print(t)
print(len(t))

# class A:

#     @classmethod
#     @manage_read_only_connection
#     def get_routes(cursor, cls):
#         stop_lat, stop_lon = 51.893842, -8.499551
#         shape_id = "4497_494"
#         query = """
#                     WITH sh1 AS (
#                         SELECT shape_pt_sequence AS stop_seq, shape_pt_lat AS lat, shape_pt_lon AS lon, shape_dist_traveled, shape_id
#                         FROM shapes AS sh1
#                         WHERE shape_id = %s
#                         ORDER BY POWER(shape_pt_lat - %s, 2) + POWER(shape_pt_lon - %s, 2)
#                         LIMIT 1
#                         ),
#                     sh2 AS (
#                         SELECT shape_pt_sequence AS stop_seq, shape_pt_lat AS lat, shape_pt_lon AS lon
#                         FROM shapes AS sh2
#                         JOIN sh1 AS sh1 ON sh2.shape_id = sh1.shape_id
#                         WHERE sh2.shape_id = %s
#                             AND sh2.shape_dist_traveled <= (sh1.shape_dist_traveled - 100)
#                         ORDER BY sh2.shape_pt_sequence DESC
#                         LIMIT 1
#                     )
#                     SELECT stop_seq, lat, lon FROM sh1
#                     UNION ALL
#                     SELECT stop_seq, lat, lon FROM sh2;
#                    """
#         query = """select table_name, column_name 
#         from information_schema.columns 
#         where table_name in (
#         select tablename from pg_tables where schemaname = 'public');""" 
#         cursor.execute(query)#, (shape_id, stop_lat, stop_lon, shape_id))
#         res = cursor.fetchall()
#         print(res)

# A.get_routes()