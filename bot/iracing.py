import aiohttp
import asyncio
import hashlib
import base64
import os
import pickle

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
                print(response.status)
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
    
    async def get_driver(self, driver_id):
        self.cookies = self.cookies or {}
        async with aiohttp.ClientSession(cookies=dict(self.cookies)) as session:
            async with session.get(f'https://members-ng.iracing.com/data/lookup/drivers?search_term={driver_id}') as response:
                
                if response.status == 200:
                    data_json = await self.click_thru_url(await response.json())
                    return data_json
                    
                if response.status == 401:
                    await self.authenticate()
                    return await self.get_driver(driver_id)
                else:
                    print(f"Failed to get driver: {await response.json()}")
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
        
        
        