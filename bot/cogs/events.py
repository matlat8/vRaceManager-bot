# import packages
import arrow
from discord.ext import commands, tasks
import os
import json


# import locals
from iracing import iRacing
from supa import Supa

class Events(commands.Cog):
    def __init__(self, bot):
        self.iracing = iRacing()
        self.bot = bot
        self.supa = Supa(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY')).get_supabase()
        self.search_for_events.start()
        
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def setnotificationchannel(self, ctx, *args):
        
        notification_options = ['hosted','offical']
        
        if not args:
            await ctx.send(f'You must provide a notification type. Valid types: {", ".join(notification_options)}')
            return
        
        if args[0] not in notification_options:
            await ctx.send(f'Invalid notification type. Valid types: {", ".join(notification_options)}')
            return
        
        self.supa.table('guilds').insert({
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
    @tasks.loop(seconds=0, minutes=5, hours= 0, count=None)
    async def search_for_events(self):
        drivers = self.supa.table('v_distinct_drivers').select('*').execute()
        start_time = arrow.utcnow().format('YYYY-MM-DDTHH:mm:ss') + 'Z'
        end_time = arrow.utcnow().shift(minutes=-6).format('YYYY-MM-DDTHH:mm:ss') + 'Z'
        insert_data = []
        for driver in drivers.data:
            print(driver['iracing_number'])
            data = await self.iracing.search_series(driver['iracing_number'], end_time, start_time)
            if not data:
                continue
            for obj in data:
                for session in obj:
                    if session['event_type'] == 5:
                        session['cust_id'] = driver['iracing_number']
                        insert_data.append(session)
                        print(f"Found session {session['subsession_id']} for driver {driver['iracing_number']} - {session['event_type']}")
                        #break
                #print(obj)
        self.insert_new_events(insert_data)  
        
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
            print(json.dumps(obj, indent=4))
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
        
        if final_insert:
            data = self.supa.table('series_entries').upsert(final_insert).execute()
            print(data)
            
    async def cog_unload(self):
        self.search_for_events.cancel()
         
        
        
    
        
        