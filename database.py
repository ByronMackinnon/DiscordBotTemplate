import aiosqlite

class DB:
    """
    Database class for managing the retrieval and editing of data within it.
    """

    class insert:
        """Subclass for managing insertion of data to the database in the event it changes."""
        def __init__(self, bot):
            self.bot = bot

    @staticmethod
    async def select(db='data.db', sql=None, variables=tuple(), chunked=False):
        """Helper method for grabbing information from database."""
        db = await aiosqlite.connect(db)
        cursor = await db.execute(sql, variables)

        if chunked:
            rows = await cursor.fetchall()
            await cursor.close()
            await db.close()

            values = [item for t in rows for item in t]

            async def chunks(lst, length): #* This is a helper function to organize the data so it returns a list of lists.
                length = max(1, length)
                return list(lst[i:i+length] for i in range(0, len(lst), length))

            chunk_length = len(sql.split(','))

            return await chunks(values, chunk_length)

        else:
            row = await cursor.fetchone()
            await cursor.close()
            await db.close()

            #* If nothing is returned - Nothing happens
            if row is None:
                pass

            #* If only a single result is returned. It gets turned to it's proper data type
            elif len(row) == 1:
                try:
                    row = int(row[0])
                except (TypeError, ValueError):
                    row = str(row[0])

            #* Otherwise it is returned as a list
            else:
                row = list(row)

            if row == "None":
                row = None

            return row

    @staticmethod
    async def update(db='data.db', sql=None, variables=tuple()):
        """Edit data from the database."""
        async with aiosqlite.connect(db) as db:
            await db.execute(sql, variables)
            await db.commit()

    @staticmethod
    async def found_in(db='data.db', sql=None, variables=tuple()) -> bool:
        """Returns a boolean based on whether or not the SQL query was able to return any data."""
        async with aiosqlite.connect(db) as db:

            async with db.execute(sql, variables) as cursor:
                check = await cursor.fetchone()
                if check is None:
                    return False
                return True