from utilities.database import db
import random

class Player():
    def __init__(self, ctx):
        self.server, self.channel, self.author = ctx.guild, ctx.channel, ctx.author
        
        # Load user data from database
        user_data = db.get_user(self.author.id)
        print(user_data)
        self.gold = user_data['gold']
        self.cheese = user_data['cheese']
        
        # Load inventory
        self.inventory = db.get_user_inventory(self.author.id)
        self.inventory = [tup[1] for tup in self.inventory]
        
        # Load server data
        server_data = db.get_server(self.server.id)
        self.vacuumcd = server_data['VacuumCD']
        
        # Items (check inventory for item IDs)
        self.linkens = ("Linken's Sphere" in self.inventory)
        self.MKB = ("Monkey King Bar" in self.inventory)
        self.shiva = ("Shiva's Guard" in self.inventory)
        self.armlet = ("Armlet of Mordiggian" in self.inventory)
        self.midas = ("Hand of Midas" in self.inventory)
        self.aegis = ("Aegis" in self.inventory)
        self.pirate_hat = ("Pirate Hat" in self.inventory)
        self.necronomicon = ("Necronomicon" in self.inventory)
        self.aeon_disk = ("Aeon Disk" in self.inventory)
    
    def unique_int_randomizer(self, length, category):
        """Generate unique random integers for quiz questions"""
        numlist = db.get_rng_numbers(self.server.id, category)
        
        # If list is getting too long, trim it
        if len(numlist) > length * 7 / 8:
            keep_count = length - round(length / 7)
            db.clear_old_rng_numbers(self.server.id, category, keep_count)
        
        n = random.randint(0, length)
        while n in numlist or n >= length:
            n = random.randint(0, length)
            for i in range(15):
                if n not in numlist:
                    break
                n += 1
        
        # Save the new number
        db.add_rng_number(self.server.id, category, n)
        
        return n
    
    def add_gold(self, newgold):
        """Add gold to user with multipliers"""
        multiplier = 1 + 0.2 * self.midas + 0.05 * self.armlet
        newgold *= multiplier
        
        # Update gold in memory and database
        self.gold += round(newgold)
        db.update_user_gold(self.author.id, self.gold)
        
        return round(newgold)

    def check_msg(self, msg):
        return msg.channel == self.channel and msg.author == self.author
    
    def set_duration(self, duration):
        """Set duration for quiz commands (30% more time if shiva is held)"""
        multiplier = 1 + 0.3 * self.shiva - 0.1 * self.armlet
        duration *= multiplier
        return round(duration)
    
    def set_lives(self, lives):
        """Set amount of lives (+1 if the user has aegis)"""
        return lives + self.aegis
    
    def set_plunder(self, plunder):
        """Increase gold if user has pirate hat (used for duel)"""
        return plunder + 10000 * self.pirate_hat
    
    def set_necro(self, nquestions):
        """Increase amount of questions if user has necronomicon (used for freeforall)"""
        return nquestions + self.necronomicon * 10
    
    def clutched(self, ncorrectanswsinarow):
        """Linkens saves one and aeon disk halves the loss"""
        if self.linkens:
            output = ncorrectanswsinarow
            self.saves -= 1
        elif self.aeon_disk:
            output = round(ncorrectanswsinarow / 2)
        else:
            output = 0
        return output