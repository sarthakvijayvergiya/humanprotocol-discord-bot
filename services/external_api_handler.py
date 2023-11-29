"""
Author Sarthak Vijayvergiya - https://github.com/sarthakvijayvergiya
Description: A Discord bot that helps in launching jobs, setting API keys, and configuring result channels for the Human Protocol.
"""

import aiohttp
import os
import json

class ExternalAPIHandler:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.base_url = os.getenv(
            "API_BASE_URL"
        )  # Read API URL from an environment variable

    async def launch_job(
        self,
        api_key,
        requesterTitle,
        submissionsRequired,
        requesterDescription,
        fundAmount,
        network_chain_id
    ):
        url = f"{self.base_url}/job/fortune"

        headers = {
            "x-api-key": api_key,  # Use the API key secret as the header value
            "Content-Type": "application/json",
        }

        payload = {
            "requesterTitle": requesterTitle,
            "submissionsRequired": int(submissionsRequired),
            "requesterDescription": requesterDescription,
            "fundAmount": int(fundAmount),
            "chainId": int(network_chain_id)
        }
        try:
            async with self.session.post(
                url, json=payload, headers=headers
            ) as response:
                if response.status == 201:
                    if response.headers.get("Content-Type") == "application/json":
                        data = await response.json()
                        return data  # You might want to return the job ID or some confirmation data
                    else:
                        response_text = await response.text()
                        print(
                            f"Expected JSON, but got a different content type: {response.headers.get('Content-Type')}"
                        )
                        print(f"Response text: {response_text}")
                        return response_text
                else:
                    response_text = await response.text()
                    print(f"Failed to launch job: {response.status} {response_text}")
                    return None
        except Exception as e:
            print(f"Error while making API request: {str(e)}")
            return None

    async def check_job_result(self, api_key, job_id):
        url = f"{self.base_url}/job/result?jobId={job_id}"

        headers = {
            "x-api-key": api_key,  # Use the API key secret as the header value
            "Content-Type": "application/json",
        }

        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    if response.headers.get("Content-Type") == "application/json":
                        data = await response.json()
                        # Assuming the API returns an array of FortuneFinalResultDto objects
                        results = []
                        for item in data:
                            result = {
                                "workerAddress": item.get("workerAddress", ""),
                                "solution": item.get("solution", ""),
                            }
                            results.append(result)
                        return results
                    else:
                        response_text = await response.text()
                        print(
                            f"Expected JSON, but got a different content type: {response.headers.get('Content-Type')}"
                        )
                        print(f"Response text: {response_text}")
                        try:
                            data = json.loads(response_text)
                            return data
                        except json.JSONDecodeError:
                        # If parsing fails, handle it as a non-JSON response
                            print(
                                f"Expected JSON, but got a different content type: {response.headers.get('Content-Type')}"
                            )
                            print(f"Response text: {response_text}")
                            return None
                else:
                    response_text = await response.text()
                    print(
                        f"Failed to check job result: {response.status} {response_text}"
                    )
                    return None
        except Exception as e:
            print(f"Error while making API request to check job result: {str(e)}")
            return None

    async def close_session(self):
        await self.session.close()
