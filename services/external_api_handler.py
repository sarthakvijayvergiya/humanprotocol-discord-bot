import aiohttp
import os

class ExternalAPIHandler:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.base_url = os.getenv('API_BASE_URL')  # Read API URL from an environment variable

    async def launch_job(self, api_key, requesterTitle, submissionsRequired, requesterDescription, fundAmount):
        url = f'{self.base_url}/job/fortune'
        
        headers = {
            'x-api-key': api_key,  # Use the API key secret as the header value
            'Content-Type': 'application/json'
        }
        
        payload = {
            "requesterTitle": requesterTitle,
            "submissionsRequired": int(submissionsRequired),
            "requesterDescription": requesterDescription,
            "fundAmount": int(fundAmount)
        }
        
        try:
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 201:
                    if response.headers.get('Content-Type') == 'application/json':
                        data = await response.json()
                        return data  # You might want to return the job ID or some confirmation data
                    else:
                        response_text = await response.text()
                        print(f"Expected JSON, but got a different content type: {response.headers.get('Content-Type')}")
                        print(f"Response text: {response_text}")
                        return response_text
                else:
                    response_text = await response.text()
                    print(f"Failed to launch job: {response.status} {response_text}")
                    return None
        except Exception as e:
            print(f"Error while making API request: {str(e)}")
            return None

    async def close_session(self):
        await self.session.close()