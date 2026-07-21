import discord
import os, asyncio
from discord.ext import commands
import utilities.quizdata as quizdata
from utilities.database import db
from utilities.helpers import strip_str

os.chdir(os.getcwd())

store_items, store_descriptions = quizdata.store_items, quizdata.store_descriptions
storekeys, storevalues = list(store_items.keys()), list(store_items.values())

def helm_of_dominator(items, price):       #give discount if userhas helm of the dominator
    if ("Helm of Dominator" in items):
        price *= 0.95
    return round(price)

class Store(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief = "See what items are available.", aliases = ["shop"])
    async def store(self, ctx):
        artifacts = ""
        for item in store_items:        #concatenates all the names and prices together to form a list of store items
            multiplier = 23 - len(item)
            multiplier2 = 9 - len(str(store_items[item]))
            artifacts = artifacts + item + (multiplier * " ") + str(store_items[item]) + (multiplier2 * " ") + store_descriptions[item] + " \n"
        await ctx.send(f"``` Item:               Price:    Description: \n{artifacts}```")

    @commands.command(brief = "Buy an item from the store.")
    async def buy(self, ctx, *, purchase):
        try:
            user = db.get_user(ctx.author.id)

            if not user:
                await ctx.send("""You haven't got any gold yet, try "322 help" and use Quiz commands to earn some.""")
                return

            user_items = db.get_user_inventory(ctx.author.id)      #get list of items the user has(they're integers)
            user_items = [tup[1] for tup in user_items]
            user_gold = user["gold"]

            purchasestr = strip_str(purchase)
            if purchasestr not in [strip_str(x) for x in storekeys]:    #store validation
                await ctx.send("That item doesn't exist.")
            elif purchasestr == "cheese":
                price = helm_of_dominator(user_items, 20000)
                if user_gold < price:
                    await ctx.send("You don't have enough gold to purchase cheese yet, it costs ``20000`` gold.")
                else:
                    db.buy_item(ctx.author.id, purchasestr, price)
                    await ctx.send("You have purchased a cheese!")
            else:                   #list of user items is stored as the item prices in json file
                itemindex = [strip_str(x) for x in storekeys].index(purchasestr)        #get the index of the item being purchased
                itemname = storekeys[itemindex]
                price = helm_of_dominator(user_items, storevalues[itemindex])
                if storevalues[itemindex] in user_items:            #if item is already bought
                    await ctx.send("You already have that item.")
                elif price > user_gold:             #if item is too expensive
                    await ctx.send(f"You don't have enough gold, this item costs {storevalues[itemindex]} gold.")
                else:               #item being purchased
                    db.buy_item(ctx.author.id, itemname, price)                
                    await ctx.send("You have purchased the item.")
        except Exception as e:
            print("store.py, buy: ", e)

    @commands.command(brief = "Sell an item from your inventory.")
    async def sell(self, ctx, *, sale):
        try:
            user = db.get_user(ctx.author.id)

            if not user:
                await ctx.send("""You haven't got any gold yet, try "322 help" and use Quiz commands to earn some.""")
                return

            soldstr = strip_str(sale)             #stripped item to be sold
            strippeditems = [strip_str(x) for x in storekeys]       #list of stripped store items
            
            user_items = db.get_user_inventory(ctx.author.id)      #get list of items the user has(they're integers)
            user_items = [tup[1] for tup in user_items]

            if soldstr == "cheese":
                if user["cheese"] <= 0:
                    await ctx.send("You don't have any cheese to sell.")
                else:
                    db.sell_item(ctx.author.id, soldstr, 15000)
                    await ctx.send(f"You have sold the cheese for ``15000`` gold.")
            elif soldstr in strippeditems:          #if item exists
                itemindex = strippeditems.index(soldstr)        #gets index to get item's cost
                itemname = storekeys[itemindex]
                sellprice = int(storevalues[itemindex]/2)
                if itemname in user_items:          #if item is inside user inventory
                    db.sell_item(ctx.author.id, itemname, sellprice)
                    await ctx.send(f"You sold the item for {sellprice} gold.")
                else:                     #if item exists but isn't in the inventory
                    await ctx.send("You don't have that item in your inventory in order to sell it.")
            else:                 #if item doesn't exist at all
                await ctx.send("That item doesn't exist in the store.")
        except Exception as e:
            print("store.py, sell: ", e)

    @commands.command(brief = "Check how much gold and cheese you own.")
    async def gold(self, ctx):
        try:
            user = db.get_user(ctx.author.id)

            if user:
                authorgold = user["gold"]
                authorcheese = user["cheese"]
                await ctx.send(f"**{ctx.author.display_name}** you currently have **``{authorgold}``** gold and ``{authorcheese}`` cheese.")
            else:
                await ctx.send("""You haven't got any gold yet, try "322 help" and use Quiz commands to earn some.""")
        except Exception as e:
            print("store.py, gold: ", e)


    @commands.command(brief = "Check your inventory.", aliases = ["inv"])
    async def inventory(self, ctx):         #check inventory
        try:
            user = db.get_user(ctx.author.id)

            if not user:
                await ctx.send("""You haven't got an inventory yet, try "322 help" and use Quiz commands to earn gold and buy items!""")
                return

            str_itemlist = db.get_user_inventory(ctx.author.id)      #get list of items the user has(they're integers)
            str_itemlist = [tup[1] for tup in str_itemlist]

            if len(str_itemlist) == 0:              #if inventory is empty
                await ctx.send("Your inventory is empty, try 322 buy to purchase items.")
            else:
                items_listed = "``, ``".join(str_itemlist)         #create a string to be put into the message
                await ctx.send(f"You have ``{items_listed}`` in your inventory.")
        except Exception as e:
            print("store.py, inv: ", e)


    @commands.command(brief = "Give someone cheese.", aliases = ["give"])
    async def givecheese(self, ctx, reciever: discord.Member, amount:int):
        try:
            giver = str(ctx.author.id)          #obtain ids of the cheese giver and reciever
            reciever = str(reciever.id)

            if giver == reciever:
                await ctx.send("Nice try.")
            elif amount == 0:
                await ctx.send("What?")
            elif amount < 0:
                await ctx.send("Are you trying to snatch cheese?.")
            elif giver not in users.keys():
                await ctx.send("You haven't got any cheese yet.")
            elif giver["cheese"] < amount:
                await ctx.send("You haven't got that much cheese.")
            elif not reciever:
                await ctx.send("That user doesn't have an inventory yet.")
            else:
                db.transfer_cheese(giver, reciever, amount)
                await ctx.send(f"You have successfully transferred {amount} cheese!")
        except Exception as e:
            print("store.py, givecheese: ", e)

    @commands.command(brief = "Delete your stats.")
    async def clearstats(self, ctx):
        try:
            await ctx.send('Are you sure you want to **CLEAR ALL** your gold and your entire inventory? Type "Confirm" to finalize')
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author		#checks if the reply came from the same person in the same channel
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
            except asyncio.TimeoutError:		#If too late
                await ctx.send("Stat clear **cancelled.**")
            else:
                if msg.content == "Confirm":
                    user = db.get_user(ctx.author.id)
                    if user:
                        db.delete_user(ctx.author.id)
                        await ctx.send("Your stats have been **successfully deleted.**")
                    else:
                        await ctx.send("There was nothing to clear.")
                else:
                    await ctx.send("Stat clear has been **cancelled.**")
        except Exception as e:
            print("store.py, clearstats: ", e)

    @buy.error
    async def buyerror(self, ctx, error):
        if isinstance (error, commands.MissingRequiredArgument):
            await ctx.send("""You need to specify what item you're purchasing, try "322 store" to see available items.""")

    @sell.error
    async def sellerror(self, ctx, error):
        if isinstance (error, commands.MissingRequiredArgument):
            await ctx.send("""You need to specify what item you're selling, try "322 inventory" to see what you have.""")

    @givecheese.error
    async def givecheeseerror(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify who you're giving to and how much cheese you're transfering, like so: 322 givecheese @user 1")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("That user doesn't exist or isn't in this server.")


    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            pass
        else:
            raise error

async def setup(bot):
    await bot.add_cog(Store(bot))
