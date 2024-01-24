# sdk_service.py
import datetime
from human_protocol_sdk.constants import ChainId
from human_protocol_sdk.escrow import EscrowUtils, EscrowFilter, Status

async def get_escrows(self, escrow_address, network_chain_id=ChainId.POLYGON_MUMBAI):
    # This function should be called after ensuring the escrow address is available (~10min after job creation)

    # Set up date filters:
    date_from = datetime.datetime.now() - datetime.timedelta(days=30)
    date_to = datetime.datetime.now()

    # Use the Human Protocol SDK to get escrows:
    escrows = EscrowUtils.get_escrows(
        EscrowFilter(
            networks=[network_chain_id],
            status=Status.Pending,  # or any other status you are interested in
            date_from=date_from,
            date_to=date_to,
            escrow_address=escrow_address  # Pass the escrow address from job details
        )
    )
    return escrows
