import sqlite3


class Database:
    def __init__(self, db_file='DotaQuiz.db'):
        self.db_file = db_file
    
    def get_connection(self):
        return sqlite3.connect(self.db_file)
    
    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # get user
        cursor.execute('SELECT Gold, Cheese FROM Players WHERE DiscordUserId = ?', (str(user_id),))
        result = cursor.fetchone()

        # create new user if there is none
        if not result:
            cursor.execute(
                'INSERT INTO Players (DiscordUserId, Gold, Cheese) VALUES (?, 10, 0)',
                (str(user_id),)
            )
            conn.commit()
            result = {'gold': 10, 'cheese': 0}
        else:
            result = {'gold': result[0], 'cheese': result[1]}
        
        conn.close()
        
        return result
    
    def get_user_inventory(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        #PlayerId, DiscordUserId, ItemId, ItemName, ItemPrice
        cursor.execute('SELECT * FROM vw_PlayerInventory WHERE DiscordUserId = ?', (str(user_id),))
        items = [row[2:] for row in cursor.fetchall()] #gets ItemId and ItemName
        
        conn.close()

        return items

    
    def update_user_gold(self, user_id, gold):
        conn = self.get_connection()
        cursor = conn.cursor()
        #set gold
        cursor.execute('UPDATE Players SET gold = ? WHERE DiscordUserId = ?', (gold, str(user_id)))
        
        conn.commit()
        conn.close()
    
    def get_server(self, guild_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT VacuumCD FROM Guilds WHERE DiscordGuildId = ?', (str(guild_id),))
        result = cursor.fetchone()
        
        # if there is no server in database
        if not result:
            cursor.execute(
                'INSERT INTO Guilds (DiscordGuildId, VacuumCD) VALUES (?, 16)',
                (str(guild_id),)
            )
            conn.commit()
            result = (16,)
        
        conn.close()
        return {'VacuumCD': result[0]}
    
    def get_rng_numbers(self, guild_id, category):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # getting all the numbers from the guild of the questiontype
        cursor.execute(
            """
                SELECT QuestionId FROM GuildRNG
                WHERE GuildId = (SELECT GuildId FROM Guilds WHERE DiscordGuildId = ?)
                AND QuestionTypeId = ?
            """,
            (str(guild_id), category)
        )
        
        numbers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return numbers
    
    def add_rng_number(self, guild_id, category, number):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT OR IGNORE INTO GuildRNG (GuildId, QuestionTypeId, QuestionId)
            VALUES ((SELECT GuildId FROM Guilds WHERE DiscordGuildId = ?), ?, ?)
            """,
            (str(guild_id), category, number)
        )
        
        conn.commit()
        conn.close()
    
    def clear_old_rng_numbers(self, guild_id, category, keep_count):
        conn = self.get_connection()
        cursor = conn.cursor()

        # clearing old rng numbers to keep it fresh
        # the EntryId integer limit is over 9 quadrillion so it's fine
        cursor.execute(
            """
            DELETE FROM GuildRNG
            WHERE EntryId IN (
                SELECT EntryId FROM (
                    SELECT EntryId,
                           ROW_NUMBER() OVER (
                               PARTITION BY GuildId, QuestionTypeId
                               ORDER BY EntryId DESC
                           ) AS rn
                    FROM GuildRNG
                    WHERE GuildId = (SELECT GuildId FROM Guilds WHERE DiscordGuildId = ?)
                      AND QuestionTypeId = ?
                )
                WHERE rn > ?
            )
            """,
            (str(guild_id), category, keep_count)
        )

        conn.commit()
        conn.close()

    def delete_guild(self, guild_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Completely nuke the guild data
        cursor.execute(
            """
            DELETE FROM GuildRNG
            WHERE GuildId = (SELECT GuildId FROM Guilds WHERE DiscordGuildId = ?)
            
            DELETE FROM Guilds
            WHERE DiscordGuildId = ?
            """,
            (str(guild_id), str(guild_id),)
        )

        conn.commit()
        conn.close()

    # lil function to quickly check if user has octarine or not
    def check_octarine(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
                SELECT 1 FROM vw_PlayerInventory WHERE DiscordUserId = ? AND ItemName = 'Octarine Core'
            """,
            (str(user_id),)
        )

        result = cursor.fetchone()

        conn.commit()
        conn.close()

        # return bool
        return bool(result)


    ### ------- Store commands

    def buy_item(self, user_id, item_name, price):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        #much simpler on cheese
        if item_name == "cheese":
            cursor.execute(
                """
                    UPDATE Players
                    SET Gold = Gold - ?,
                        Cheese = Cheese + 1
                    WHERE DiscordUserId = ?
                """,
                (price, str(user_id),))
        else:
            cursor.execute(
                """
                    INSERT OR IGNORE INTO Inventories (PlayerId, ItemId)
                    VALUES (
                        (SELECT PlayerId FROM Players WHERE DiscordUserId = ?),
                        (SELECT ItemId FROM Items WHERE ItemName = ?)
                    )
                """,
                (str(user_id), item_name)
            )
            cursor.execute(
                """
                    UPDATE Players
                    SET Gold = Gold - ?
                    WHERE DiscordUserId = ?
                """,
                (price, str(user_id))
            )
        
        conn.commit()
        conn.close()
    
    def sell_item(self, user_id, item_name, price):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        #much simpler on cheese
        if item_name == "cheese":
            cursor.execute(
                """
                    UPDATE Players
                    SET Gold = Gold + ?,
                        Cheese = Cheese - 1
                    WHERE DiscordUserId = ?
                """,
                (price, str(user_id)))
        else:
            cursor.execute(
                """
                    DELETE FROM Inventories
                    WHERE PlayerId = (SELECT PlayerId FROM Players WHERE DiscordUserId = ?)
                    AND ItemId = (SELECT ItemId FROM Items WHERE ItemName = ?)
               """,
                (str(user_id), item_name)
            )
            
            cursor.execute(
                """
                    UPDATE Players
                    SET Gold = Gold + ?
                    WHERE DiscordUserId = ?
                """,
                (price, str(user_id),)
            )
        
        conn.commit()
        conn.close()

    def transfer_cheese(self, sender_id, reciever_id, amount):
     
        conn = self.get_connection()
        cursor = conn.cursor()
        
        #all the technical checks are done in store.py
        cursor.execute(
            """
                UPDATE Players
                SET Cheese = Cheese - ?
                WHERE DiscordUserId = ?

                UPDATE Players
                SET Cheese = Cheese + ?
                WHERE DiscordUserId = ?
            """,
            (amount, str(sender_id), amount, str(reciever_id),)
        )
        
        conn.commit()
        conn.close()

    def delete_user(self, user_id):
        # Completely nuking the user data
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
                DELETE FROM Players
                WHERE DiscordUserId = ?
            """,
            (str(user_id),)
        )

        # clearing the items
        cursor.execute(
            """
                DELETE FROM Inventories
                WHERE PlayerId = (SELECT PlayerId FROM Players WHERE DiscordUserId = ?)
            """,
            (str(user_id),)
        )
        
        
        conn.commit()
        conn.close()


    ### ------- Miscellaneous commands

    def update_vacuumcd(self, guild_id, seconds):
        # the added seconds are randomised in miscellanous.py
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
                        SELECT VacuumCD FROM Guilds WHERE DiscordGuildId = ?
                    """,
                        (str(guild_id),))
        result = cursor.fetchone()
        
        #add server for the first time
        if not result:
            cursor.execute(
                'INSERT INTO Guilds (DiscordGuildId, VacuumCD) VALUES (?, 16)',
                (str(guild_id),)
            )
            conn.commit()
            result = 16 + seconds
        else: # just change the vacuumcd
            cursor.execute(
                """
                    UPDATE Guilds
                    SET VacuumCD = VacuumCD + ?
                    WHERE DiscordGuildId = ?
                """,
                (seconds, str(guild_id),)
            )

            result = result[0] + seconds
        
        conn.commit()
        conn.close()

        return result

    def get_cheeseboard(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # get top 10 users
        cursor.execute('SELECT DiscordUserId, Cheese FROM Players ORDER BY Cheese DESC LIMIT 10')
        result = cursor.fetchall()
        
        conn.close()
        
        return result



db = Database('DotaQuiz.db')