import random
import discord
import os, json
from discord.ext import commands
import utilities.quizdata as quizdata
from utilities.database import db
from utilities.helpers import strip_str

os.chdir(os.getcwd())

copypastas, copypastainfo = quizdata.copypastas, quizdata.copypastainfo

#embed of list of pastas to display
pastas = []
for key, value in copypastainfo.items():
    pastas.append(key + "   ––––	" + value)
pastalist = discord.Embed(colour=0x9b59b6)
pastalist.add_field(name="Copypastas:", value="\n".join(pastas), inline=False)

class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief = "See the top 10 cheese collectors.", aliases = ["board"])
    async def cheeseboard(self, ctx):
        try:
            cheesers = db.get_cheeseboard()

            onlycheese = {k[0]: k[1] for k in cheesers}         #create a dict of user ids and their cheese
            sort = {k: v for k, v in sorted(onlycheese.items(), key=lambda item: item[1], reverse=True)}      #sort the dictionary according to cheese amounts
            sortkeys, sortvalues = list(sort.keys()), list(sort.values())       #obtain lists of the keys and values for later use
            basetext = "Collector:                         Cheese amount:\n"
            for n in range(0, 10):
                user = ctx.guild.get_member(int(sortkeys[n]))
                if type(user) == discord.Member:        #if user is in the server it will display the name
                    multiplier = 44 - len(user.display_name)
                    if n == 9:          #if it's the 10th user it will be less indented to be in line with other users
                        basetext = basetext + str(n+1) + ")" + user.display_name + " "*(multiplier-1) + str(sortvalues[n])
                    else:
                        basetext = basetext + str(n+1) + ")" + user.display_name + " "*multiplier + str(sortvalues[n]) + "\n"
                else:           #otherwise it will just say "hidden" instead
                    if n == 9:        #if it's the 10th user it will be less indented to be in line with other users
                        basetext = basetext + str(n+1) + ")[Hidden User]" + " "*30 + str(sortvalues[n])
                    else:
                        basetext = basetext + str(n+1) + ")[Hidden User]" + " "*31 + str(sortvalues[n]) + "\n"
            await ctx.send(f"```{basetext}```")
        except Exception as e:
            print("miscallaneous.py: ", e)

    @commands.command(brief = "Get a copy of a DotA copypasta.", aliases = ["pasta"])
    async def copypasta(self, ctx, pasta):
        try:
            if strip_str(pasta) in list(copypastas.keys()):
                await ctx.send(copypastas[strip_str(pasta)])
            else:
                await ctx.send("That is not one of the available copypastas: ", embed=pastalist)
        except Exception as e:
            print("miscallaneous.py: ", e)

    @commands.command()
    async def hohoohahaa(self, ctx):
        await ctx.send(file=discord.File('snoper.png'))

    @commands.command()
    async def newpatch(self, ctx):
        try:
            vacuumcd = db.update_vacuumcd(ctx.guild.id, random.randint(1, 3))
            await ctx.send(f"""Vacuum cooldown has been increased, it is now **{vacuumcd}** seconds long.""")
        except Exception as e:
            print("miscallaneous.py: ", e)

    @commands.command()
    async def missedhook(self, ctx):
        await ctx.send(f"""You missed your hook **because** the ping is {round(self.bot.latency * 1000)}ms""")

    @copypasta.error
    async def copypastaerror(self, ctx, error):
        if isinstance (error, commands.MissingRequiredArgument):
            await ctx.send("You need to specify which copypasta you want like so: 322 copypasta <pasta> out of one of these copypastas: ", embed=pastalist)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            pass
        else:
            raise error

async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
