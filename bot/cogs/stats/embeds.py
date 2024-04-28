import discord

class StatsEmbeds():
    def stats_help(self):
        embed = discord.embeds.Embed(title='Stats Help')
        embed.add_field(name='laps_per_track', value='Shows the number of laps driven on each track.')
        return embed
    
    
    def laps_per_track(self, data):
        embed = discord.embeds.Embed(title='Laps per Track')
        for row in data:
            embed.add_field(name=row['track_name'], value=row['laps_driven'])
        return embed