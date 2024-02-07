# sdk_service.py
import datetime
from human_protocol_sdk.constants import ChainId
from human_protocol_sdk.escrow import EscrowUtils
from human_protocol_sdk.filter import EscrowFilter, Status
import os
import json

async def get_escrows():
    # This function should be called after ensuring the escrow address is available (~10min after job creation)

    supported_networks_str = os.getenv("SUPPORTED_NETWORKS", "{}")
    supported_networks = json.loads(supported_networks_str)

    # Extract all chain IDs from the supported networks
    network_chain_ids = []
    # Iterate over the names in the supported networks
    for network_name in supported_networks.keys():
        try:
            # Attempt to convert each network name to the corresponding ChainId enum
            # by matching the network name with the enum member name
            enum_value = ChainId[network_name.upper()]
            network_chain_ids.append(enum_value)
        except KeyError:
            # If a network name does not match any enum member name, skip it
            continue
    # Set up date filters:
    date_from = datetime.datetime.now() - datetime.timedelta(days=90)
    date_to = datetime.datetime.now()

    # Use the Human Protocol SDK to get escrows:
    escrows = EscrowUtils.get_escrows(
        EscrowFilter(
            networks=[ChainId.POLYGON_MUMBAI],
            status=Status.Complete,  # or any other status you are interested in
            date_from=date_from,
            date_to=date_to,
        )
    )
    return escrows
