#!/bin/python
from sqlalchemy import create_engine,inspect
from pypika import Query, Table, Field
import logging


class DBConnection:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.inspector = inspect(self.engine)

    def get_table_metadata(self, table_name):
        return self.inspector.get_columns(table_name)

    def execute(self, sql):
        self.engine.execute(sql)

    def query(self, sql):
        return self.engine.execute(sql).fetchall()

    def upsert(self, table_name, content, update_content):
        # one by one
        #print(content)
        the_table = Table(table_name)
        a = Query.into(the_table).columns(*list(content.keys())) \
            .insert(*list(content.values()))

        try:
            self.engine.execute(a.get_sql())
            logging.info(a.get_sql())
        except Exception as inst:
            #update
            the_table = Table(table_name)

            #todo@rain
            unique_keys = self.get_table_unique_keys(table_name)
            query_id_by_keys = Query.from_(the_table) \
                .select('id')

            for one_key in unique_keys:
                query_id_by_keys = query_id_by_keys.where(getattr(the_table, one_key) == content[one_key])

            result = self.engine.execute(query_id_by_keys.get_sql()).fetchall()
            if len(result) > 1:
                logging.error("invalid result %s, with query string %s" % (str(result), query_id_by_keys.get_sql()))
                raise Exception('invalid result')
            else:
                the_id = result[0]['id']
                the_query = Query.update(the_table).where(the_table.id == the_id)
                #todo@rain: handle update_content is null
                for key in update_content:
                    the_query = the_query.set(key, update_content[key])

                self.execute(the_query.get_sql())
                logging.info(the_query.get_sql())

    def query_id_by_foreign_key(self, table_name, foreign_key, value):
        the_table = Table(table_name)
        query_string = Query.from_(the_table).select('id').where(getattr(the_table, foreign_key) == value)
        logging.debug("the query string is %s" % query_string)
        result = self.engine.execute(query_string.get_sql()).fetchall()
        if len(result) != 1:
            logging.error("result is not valid %s with query string %s" % (str(result), query_string.get_sql()))
        else:
            if 'id' in result[0]:
                return result[0]['id']
            else:
                raise Exception('can\'t find id in result')

    def get_table_unique_keys(self, table_name):
        all_constraints = self.inspector.get_unique_constraints(table_name)
        if all_constraints and len(all_constraints) == 1:
            return all_constraints[0]['column_names']
        else:
            raise Exception("we can only handle one unique index")




