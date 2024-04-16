import discord
import arrow


class DriverEmbed():
    
    def member_recent_race(self, data):
        # Prepare data
        start_time = arrow.get(data['session_start_time']).format('YYYY-MM-DD HH:mm')
        pos_gain_loss = data['start_position'] - data['finish_position']
        
        # Create embed
        embed = discord.Embed(title=data['series_name'], color=0x00ff00)

        embed.add_field(name='Series', value=data['series_name'], inline=False)
        embed.add_field(name='Track', value=data['track']['track_name'], inline=False)
        embed.add_field(name='Start Time', value=start_time, inline=True)
        embed.add_field(name='Winner', value=data['winner_name'], inline=True)
        embed.add_field(name='SoF', value=data['strength_of_field'], inline=False)
        embed.add_field(name='Position', value=f"{data['start_position']} ➡️ {data['finish_position']} ({'+' if pos_gain_loss > 0 else ''}{pos_gain_loss})", inline=True)
        embed.add_field(name='Laps', value=data['laps'], inline=True)
        embed.add_field(name='Laps Led', value=data['laps_led'], inline=True)
        embed.add_field(name='', value='', inline=False)
        embed.add_field(name='+/- iRating', value=data['newi_rating'] - data['oldi_rating'], inline=True)
        #embed.add_field(name='+/- Safety Rating', value=data['new_sub_level'] - data['old_sub_level'], inline=True)
        
        return embed
        


