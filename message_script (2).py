import asyncio
import nest_asyncio
import random
import sys
import pyzeebe 

nest_asyncio.apply()

async def main(message_name, message_correlation_key=""):
    channel = pyzeebe.create_camunda_cloud_channel(client_id="rBNAuQ9b9w3_wQYrNn.nHp6kC762XRGB", 
                                                        client_secret="",
                                                        cluster_id="c8192281-1489-423b-8f9e-bd82cfd54dbb",
                                                        region="dsm-1"

    )
    print("channel created")
    client = pyzeebe.ZeebeClient(channel)
    print("client connected")

    print(f"Pushing message {message_name} with ck {message_correlation_key}")

    await client.publish_message(name=message_name, correlation_key=message_correlation_key)

if (len(sys.argv) <= 1):
    print("Message Name and optional correlation key missing...")
elif (len(sys.argv) == 2):
    asyncio.run(main(sys.argv[1]))
else:
    asyncio.run(main(sys.argv[1], sys.argv[2]))

print("end")
# start "Customer arrived": Message_CustomerArrived
