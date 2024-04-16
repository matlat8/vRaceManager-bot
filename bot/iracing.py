import aiohttp
import asyncio
import hashlib
import base64
import os
import pickle
import arrow
import json

class iRacing:
    def __init__(self):
        self.cookies = None
        #self.authenticate()
    
    async def authenticate(self):
        
        body = {'email': os.environ.get("IRACING_USERNAME"), 'password': await self.encode_pw()}
        print('we just authenticated!')
        
        async with aiohttp.ClientSession() as session:
            async with session.post('https://members-ng.iracing.com/auth', data=body) as response:
                self.cookies = {c.key: c.value for c in session.cookie_jar}
                #print(await response.text())
                
    async def encode_pw(self):
        username = os.environ.get("IRACING_USERNAME")
        password = os.environ.get("IRACING_PASSWORD")
        
        initialHash = hashlib.sha256((password + username.lower()).encode('utf-8')).digest()
        hashInBase64 = base64.b64encode(initialHash).decode('utf-8')
        return hashInBase64
        
    async def click_thru_url(self, jsonobj):
        async with aiohttp.ClientSession(cookies=dict(self.cookies)) as session:
                async with session.get(jsonobj['link']) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Failed to click through URL: {response.status}")
                        return {}
                    
    async def unchunk_url(self, chunk_info):
        """Returns json object of all json chunks from the chunk_info json block provided

        Args:
            chunk_info (json): iRacing API response of the "chunk_info" json object.

        Returns:
            json: returns combined json of json responses from API
        """
        data_list = []
        async with aiohttp.ClientSession(cookies=dict(self.cookies)) as session:
            for chunk in chunk_info['chunk_file_names']:
                async with session.get(chunk_info['base_download_url'] + chunk) as response:
                    if response.status == 200:
                        data_list.append(await response.json())
                    else:
                        print(f"Failed to pass through URL: {response.status}")
                        return []
            return data_list
    
    async def get_driver(self, search_term):
        """gets basic driver information from iRacing's API
        using either their iRacing ID or their name

        Args:
            search_term (str): iRacing ID or driver name

        Returns:
            json: json object containing driver information
        """
        self.cookies = self.cookies or {}
        async with aiohttp.ClientSession(cookies=dict(self.cookies)) as session:
            async with session.get(f'https://members-ng.iracing.com/data/lookup/drivers?search_term={search_term}') as response:
                
                if response.status == 200:
                    data_json = await self.click_thru_url(await response.json())
                    return data_json
                    
                if response.status == 401:
                    await self.authenticate()
                    return await self.get_driver(search_term)
                else:
                    print(f"Failed to get driver: {await response.json()}")
                    return {} 
                
    async def get_driver_profile(self, cust_id):
        async with aiohttp.ClientSession(cookies=dict(self.cookies)) as session:
            async with session.get(f'https://members-ng.iracing.com/data/member/profile?cust_id={cust_id}') as response:
                if response.status == 200:
                    data_json = await self.click_thru_url(await response.json())
                    print(data_json)
                    return data_json
                else:
                    print(f"Failed to get driver profile: {response.status}")
                    return {}
        
                
    async def does_driver_exist(self, driver_id) -> bool: 
        """Check if a driver exists in the iRacing database

        Args:
            driver_id (int): iracing customer id

        Returns:
            bool: True if driver exists, False if driver does not exist
        """
        
        driver = await self.get_driver(driver_id)
        
        if driver == {}:
            return False
        else:
            print(driver[0]['display_name'])
            return True
        
    async def search_series(self, cust_id, start_time, end_time):
        """Gets events from iRacing's API. Specify your start and end times and the customer ID and all the latest events will return in JSON form

        Args:
            cust_id (int): cust_id of iracing memeber
            start_time (date): start time of events. Should be a prior date
            end_time (date): end time of events. Typically is the current date
        """
        self.cookies = self.cookies or {}
        async with aiohttp.ClientSession(cookies=dict(self.cookies)) as session:
            params = {
                'cust_id': cust_id,
                'finish_range_begin': start_time,#.format('YYYY-MM-DDTHH:mm:ssZZ'),
                'finish_range_end': end_time#.format('YYYY-MM-DDTHH:mm:ssZZ')
            }
            async with session.get('https://members-ng.iracing.com/data/results/search_series', params=params) as response:
                if response.status == 200:
                    json_response = await response.json()
                    data = await self.unchunk_url(json_response['data']['chunk_info'])
                    #print(data)
                    return data
                if response.status == 401:
                    await self.authenticate()
                    await self.search_series(cust_id, start_time, end_time)
        
    async def get_drivers_latest_races(self, cust_id):
        """Gets the latest races from iRacing's API and returns the JSON response
        
        Args:
            cust_id (int): iRacing customer ID
            
        Returns: 
            json: JSON response of the drivers latest races
        """
        
        self.cookies = self.cookies or {}
        
        async with aiohttp.ClientSession(cookies=dict(self.cookies)) as session:
            params = {
                'cust_id': cust_id
            }
            async with session.get("https://members-ng.iracing.com/data/stats/member_recent_races", params=params) as response:
                if response.status == 401:
                    await self.authenticate()
                    await self.get_drivers_latest_races(cust_id)
                if response.status != 200:
                    print(f'Error fetching users {cust_id} latest race from iRacing API: {response.status}')
                    
                latest_races = await self.click_thru_url(await response.json())
                #print(json.dumps(latest_races, indent=4))
                
                return latest_races
    async def subsession_lapdata(self, subsession_id):
        """Gets lap data from a specific subsession ID

        Args:
            subsession_id (int): iRacing subsession ID

        Returns:
            json: JSON response of the lap data
        """
        def add_attributes(data, subsession_id, simsession_number):
            #print(data)
            for obj in data:
                for lap in obj:
                    lap['subsession_id'] = subsession_id
                    lap['simsession_number'] = simsession_number
            return data
        
        self.cookies = self.cookies or {}
        simsessions = [-2, -1, 0]
        await self.authenticate()
        data = []
        for simsession in simsessions:
            async with aiohttp.ClientSession(cookies=dict(self.cookies)) as session:
                params = {'subsession_id': subsession_id, 'simsession_number': simsession}
                async with session.get(f"https://members-ng.iracing.com/data/results/lap_chart_data", params=params) as response:
                    print(response.status)
                    if response.status == 401:
                        print('we need to reauth')
                        await self.authenticate()
                        return await self.subsession_lapdata(subsession_id)
                    if response.status == 404:
                        print(f'unable to find subsession lap data for subsession {subsession_id}, simsession 0')
                        #continue
                    if response.status == 200:
                        link_all_laps = await self.click_thru_url(await response.json())
                        lap_data = await self.unchunk_url(link_all_laps['chunk_info'])
                        add_attributes(lap_data, subsession_id, simsession)
                        for chunk in lap_data:
                            data.append(chunk)
                    else:
                        print(f"Failed to get subsession lap data: {response.status} {await response.text()}")
                        break
                        #return {}
                
        return data
        
    async def get_member_recent_races(self, cust_id):
        await self.authenticate()
        self.cookies = self.cookies or {}
        params = {'cust_id': cust_id}
        async with aiohttp.ClientSession(cookies=dict(self.cookies)) as session:
            async with session.get(f"https://members-ng.iracing.com/data/stats/member_recent_races", params=params) as response:
                print(response.status)
                if response.status != 200:
                    await self.authenticate()
                    await self.get_member_recent_races(cust_id)
                if response.status == 200:
                    print(await response.json())
                    return await self.click_thru_url(await response.json())
        