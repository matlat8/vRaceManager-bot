import discord


class DriverEmbed():
    
    def member_recent_race(self, data):
        # Prepare data
        
        # Create embed
        embed = discord.Embed(title=data['series_name'], color=0x00ff00)
        embed.set_author(name=data['display_name'])

        embed.add_field(name='Series', value=data['series_name'], inline=False)


