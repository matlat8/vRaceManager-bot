# import packages
import arrow
from discord.ext import commands, tasks
import discord
import os
import json
import datetime



# import locals
from iracing import iRacing
from supa import Supa
from version import __version__

class Events(commands.Cog):
    def __init__(self, bot):
        self.iracing = iRacing()
        self.bot = bot
        self.supa = Supa(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY')).get_supabase()
        self.search_for_events.start()
        
    class embeds():
        def session_completed(self, data):
            start_time = arrow.get(data['start_time']).format('YYYY-MM-DD HH:mm')
            end_time = arrow.get(data['end_time']).format('YYYY-MM-DD HH:mm')
            pos_plusneg = data['starting_position'] - data['finish_position']
            
            time_delta = datetime.timedelta(seconds=data['event_best_lap_time'] / 10000)
            minutes = time_delta.seconds // 60
            seconds = time_delta.seconds % 60
            milliseconds = time_delta.microseconds // 1000
            
            
            embed = discord.Embed(title=f"{data['series_name']} - {data['subsession_id']}", color=0x00ff00)
            
            embed.set_author(name=data['display_name'], icon_url='https://imgresizer.eurosport.com/unsafe/2560x1440/filters:format(jpeg)/origin-imgresizer.eurosport.com/2016/09/08/1928257-40560625-2560-1440.jpg')
            
            embed.add_field(name="Series", value=data['series_name'], inline=False)
            embed.add_field(name="Track", value=f"{data['track']['track_name']} - {data['track']['config_name']}", inline=False)
            embed.add_field(name="Start Time", value=start_time, inline=True)
            embed.add_field(name="End Time", value=end_time, inline=True)
            embed.add_field(name='Winner', value=f"{data['winner_name']}", inline=False)
            embed.add_field(name="Position", value=f"{data['starting_position']} -> {data['finish_position']} ({'+' if pos_plusneg > 0 else ''}{pos_plusneg})", inline=True)
            embed.add_field(name="Fastest Lap", value=f"{minutes}:{seconds:02}.{milliseconds:03}", inline = True)
            embed.add_field(name="SoF", value=data['event_strength_of_field'], inline=True)
            embed.add_field(name='Laps', value=data['laps_complete'], inline = True)
            embed.add_field(name='Led Laps', value=data['laps_led'], inline = True)
            embed.add_field(name='Incidents', value=data['incidents'], inline = True)
            
            embed.set_footer(text=f"Subsession ID: {data['subsession_id']} - Current UTC: {arrow.utcnow().format('YYYY-MM-DD HH:mm')}")
            return embed
        
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def setnotificationchannel(self, ctx, *args):
        
        notification_options = ['hosted','official']
        
        if not args:
            await ctx.send(f'You must provide a notification type. Valid types: {", ".join(notification_options)}')
            return
        
        if args[0] not in notification_options:
            await ctx.send(f'Invalid notification type. Valid types: {", ".join(notification_options)}')
            return
        
        self.supa.table('guilds').update({
            f'{args[0]}_channel_id': ctx.channel.id
        }).eq('guild_id', ctx.guild.id).execute()
        await ctx.send(f'{args[0]} notifcation channel set to {ctx.channel.name}')

    @commands.command()
    async def getresults(self, ctx):
        pass
    
    @commands.command()
    async def gethostedresults(self, ctx):
        pass

    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def createhostedevent(self, ctx, cust_id = None ,*args):
        event_name = ' '.join(args[1:])
        self.supa.table('hostedsessions_to_scan').insert({
            'session_name': event_name,
            'host_cust_id': cust_id,
            'has_been_found': False,
            'requestor_discord_id': ctx.author.id
        }).execute()
        await ctx.send(f'Now searching for event {event_name}. Results will show when the session concludes.')
    
    
    async def create_hosted_event(ctx, subsession_id):
        
        pass

    #@commands.command()
    @tasks.loop(seconds=0, minutes=4, hours= 0, count=None)
    async def search_for_events(self):
        print(f"{arrow.utcnow().format('YYYY-MM-DD HH:mm:ss')} - Start of official race data pull.")
        drivers = self.supa.table('v_distinct_drivers').select('*').execute()
        end_time = arrow.utcnow().format('YYYY-MM-DDTHH:mm:ss') + 'Z'
        start_time = arrow.utcnow().shift(minutes=-50).format('YYYY-MM-DDTHH:mm:ss') + 'Z'
        insert_data = []
        iterations = 0
        for driver in drivers.data:
            iterations += 1
            #print(driver['iracing_number'])
            data = await self.iracing.search_series(driver['iracing_number'], start_time, end_time)
            if not data:
                continue
            for obj in data:
                for session in obj:
                    if session['event_type'] == 5:
                        #print(json.dumps(session, indent=4))
                        session['cust_id'] = driver['iracing_number']
                        session['display_name'] = driver['driver_name']
                        insert_data.append(session)
                        await self.send_race_completion_message(session)
                        
                        print(f"Found session {session['subsession_id']} for driver {driver['iracing_number']} - {session['event_type']}")
                        #break
                #print(obj)
        self.insert_new_events(insert_data)  
        print(iterations)
        
    @search_for_events.before_loop
    async def search_for_events_before(self):
        await self.bot.wait_until_ready()  
    
    @tasks.loop(minutes=10)
    async def search_for_hosted_events(self):
        sessions = self.supa.table('hostedsessions_to_scan').select().eq('has_been_found', False).execute()
        for session in sessions:
            if not session['has_been_found']:
                if await self.iracing.get_events(session['host_cust_id'], start_time=None, end_time=None):
                    self.supa.table('hostedsessions_to_scan').update({
                        'has_been_found': True
                    }).eq('session_name', session['session_name']).execute()
                    await ctx.send(f'Event {session["session_name"]} has been found.')
                else:
                    await ctx.send(f'Event {session["session_name"]} has not been found.')

    def insert_new_events(self, data):
        final_insert = []
        for obj in data:
            #print(json.dumps(obj, indent=4))
            row = {
                'session_id': obj['session_id'],
                'subsession_id': obj['subsession_id'],
                'cust_id': obj['cust_id'], 
                'series_id': obj['series_id'],
                'event_type': obj['event_type_name'],
                'license_category': obj['license_category'],
                'car_name': obj['car_name'],
                'num_drivers': obj['num_drivers'],
                'laps_led': obj['laps_led'],
                'laps_completed': obj['laps_complete'],
                'incidents': obj['incidents'],
                'start_time': obj['start_time'],
                'end_time': obj['end_time'],
                'track_name': f"{obj['track']['track_name']} - {obj['track']['config_name']}",
                'champ_points': obj['champ_points'] 
            }
            final_insert.append(row)
        
        #print(final_insert)
        if final_insert:
            data = self.supa.table('series_entries').upsert(final_insert).execute()
            #print(data)
            
    async def send_race_completion_message(self, session):
        guild_ids = self.supa.table('drivers').select('guild_id').eq('iracing_number', session['cust_id']).execute()
        is_notified = self.supa.table('series_entries').select('is_notified').eq('subsession_id', session['subsession_id']).execute()
        if is_notified.data and (is_notified.data[0]['is_notified'] == False or is_notified.data[0]['is_notified'] is None):
            for guild in guild_ids.data:
                channel_id = self.supa.table('guilds').select('official_channel_id').eq('guild_id', guild['guild_id']).execute()
                if not channel_id.data:
                    continue
                
                channel_id_data = channel_id.data[0]
                channel = await self.bot.fetch_channel(channel_id_data['official_channel_id'])
                #print(channel)
                await channel.send(embed=self.embeds().session_completed(session))
                self.supa.table('series_entries').update({'is_notified': True}).eq('subsession_id', session['subsession_id']).execute()
        else:
            print(f'{session["subsession_id"]} has already been notified.')
            
        
        #print(guild_ids.data)
        pass
            
    async def cog_unload(self):
        self.search_for_events.cancel()
         
        
        
    
        
        