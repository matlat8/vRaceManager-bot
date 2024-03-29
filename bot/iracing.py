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
        
        