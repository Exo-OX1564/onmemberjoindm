import discord, os, asyncio, logging, sys, json
from discord.ext import commands, tasks
from discord_webhook import DiscordWebhook, DiscordEmbed


client = commands.Bot(command_prefix="$", intents = discord.Intents.all())

#For Unverified Bots.
client = commands.Bot(command_prefix = "$", intents = discord.Intents.all())

"""
#For Verified Bots:
_i = discord.Intents.default()
_i.members = True
#_i.presences = True
#Only enable above if you have it enabled.
client = commands.Bot(command_prefix = commands.when_mentioned, intents = _i)
#client = commands.AutoShardedBot(command_prefix = commands.when_mentioned, intents = _i, shard_count = 1)
#Only enable above and remove existing client if your bot needs sharding, and then add the appropriate shard count needed. 3k servers = 3 shards, 4k servers = 4 shards, etc.
"""

with open("./config.json", "r") as file:
  config = json.load(file)
  embedFooterText = config["embedFooterText"]
  embedFootericonURL = config['embedFootericonURL']
  embedImageURL = config['embedImageURL']
  embedThumbnailURL = config['embedThumbnailURL']
  botToken = config['token'] 
  webhookURL = config['webhookURL']

class _AnsiColorizer(object):
    _colors = dict(black=30, red=31, green=32, yellow=33,
                   blue=34, magenta=35, cyan=36, white=37)

    def __init__(self, stream):
        self.stream = stream

    @classmethod
    def supported(cls, stream=sys.stdout):
        if not stream.isatty():
            return False  
        try:
            import curses
        except ImportError:
            return False
        else:
            try:
                try:
                    return curses.tigetnum("colors") > 2
                except curses.error:
                    curses.setupterm()
                    return curses.tigetnum("colors") > 2
            except:
                raise
                return False

    def write(self, text, color):

        color = self._colors[color]
        self.stream.write('\x1b[%s;1m%s\x1b[0m' % (color, text))

class ColorHandler(logging.StreamHandler):
    def __init__(self, stream=sys.stderr):
        super(ColorHandler, self).__init__(_AnsiColorizer(stream))

    def emit(self, record):
        msg_colors = {
            logging.DEBUG: "green",
            logging.INFO: "blue",
            logging.WARNING: "yellow",
            logging.ERROR: "red"
        }

        color = msg_colors.get(record.levelno, "blue")
        self.stream.write(record.msg + "\n", color)


logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(ColorHandler())

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
for handler in LOG.handlers:
    LOG.removeHandler(handler)

LOG.addHandler(ColorHandler())


@client.event
async def on_connect():
  logging.info('[INFO] [Connected to the API.]')

@client.event
async def on_ready():
  await client.change_presence(status= discord.Status.online, activity = discord.Game(name="A status here..."))
  logging.debug(f"[INFO] {client.user} is online.")


  


@client.event
async def on_member_join(member):
  try:
    #Start Making Embed Here.
    dmEmbed = discord.Embed(title="Embed title", description = "A description here with an emoji. :thumbsup: Custom emojis are supported.", color = 0xFF0000) # Change the description, title as you wish. The hex code will be after the 0x
    dmEmbed.set_image(url=embedImageURL) #Set the bots image of embed in config.json [embedImageURL]
    dmEmbed.set_thumbnail(url=embedThumbnailURL or "https://media.discordapp.net/attachments/980486928472342558/1019661366296051752/unknown.png") #Set embed thumbnail icon URL in config.json [embedThumbnailURL] 
    #Embed stops here, don't mess anything up below. 
    
    #------------[END OF EMBED]-----------

    
    logging.debug(f'[INFO] New Member Join: [{member}] {member.guild.name} - Attempting DM.')
    await member.send(embed=dmEmbed)
    logging.debug(f'[SUCCESS] DMed: {member} | [{member.id}]')
    hook = DiscordWebhook(url=webhookURL, username="Welcome DM Logger")
    embed = DiscordEmbed(
    title="Successful DM:", description=f"```\n{member} was successfully DM'ed. They joined the server: {member.guild.name}\n```", color=0x32CD32
    )
    embed.set_footer(text=f"Member ID: {member.id}")
    hook.add_embed(embed)
    response = hook.execute()
    with open('successdms.txt', 'a') as file:
      file.write(f"{member}\n")
    await asyncio.sleep(.7)
  except discord.HTTPException:
    logging.error(f"[IGNORING] Cannot DM: [{member}] | [{member.id}] - DMs Closed Or Bot.")
    whook = DiscordWebhook(url=webhookURL, username = "Welcome DM Logger")
    emb = DiscordEmbed(
      title= "Failed DM:", description = f"```\nCannot DM {member} | DM's closed or bot\n```", color = 0xFF0000  
    )
    emb.set_footer(text=f"Member ID: {member.id}")
    whook.add_embed(emb)
    resp = whook.execute()
    with open('faileddms.txt', 'a') as file:
      file.write(f"{member}\n")
    await asyncio.sleep(.7)
  except Exception as BroadException:
    logging.error(f"[ERROR] An error was raised: {BroadException}")


@client.command()
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def successdms(ctx):
  try:
    await ctx.send(file=discord.File(r'./successdms.txt'), content = "All successfull dm's are listed below:")
  except Exception as exc:
    logging.error(f"[ERROR] An error occured: {exc}")

@client.command()
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def faileddms(ctx):
  try:
    await ctx.send(file=discord.File(r'./faileddms.txt'), content = "All failed dm's are listed below:")
  except Exception as exc:
    logging.error(f"[ERROR] An error occured: {exc}")

if __name__ == '__main__':
  client.run(botToken)
