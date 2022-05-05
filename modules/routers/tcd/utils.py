import httpx
import os
import json
from loguru import logger
from pydantic import parse_obj_as
from robonomicsinterface import RobonomicsInterface

from modules.routers.tcd.models import IPFSGatewayResponse, ProtocolData


IPFS_GATEWAY_HOST = os.getenv("IPFS_GATEWAY_HOST")


async def convert_protocol(protocol: ProtocolData) -> bytes:
    return json.dumps(protocol.dict(), default=str).encode("utf-8")


async def post_to_datalog(content: str) -> str:
    """echo provided string to the Robonomics datalog"""
    logger.info(f"Posting data '{content}' to Robonomics datalog")
    txn_hash: str = RobonomicsInterface(seed=os.getenv("ROBONOMICS_SEED")).record_datalog(content)
    logger.info(f"Data '{content}' has been posted to the Robonomics datalog. {txn_hash=}")
    return txn_hash


async def push_to_ipfs_gateway(protocol: ProtocolData, username: str) -> IPFSGatewayResponse:
    """Push protocol to IPFS Gateway, returns IPFS Hash and Robonomics substrate TXN Hash"""
    logger.info(f"Pushing protocol {protocol.protocol_id} to IPFS and Robonomics datalog")
    protocol_raw = {"file_data": await convert_protocol(protocol=protocol)}
    try:
        if not IPFS_GATEWAY_HOST:
            raise ValueError("IPFS_GATEWAY_HOST not provided")
        async with httpx.AsyncClient() as client:
            raw_response = await client.post(
                IPFS_GATEWAY_HOST + "/upload-file", files=protocol_raw, headers={"username": username}
            )
            parsed_response = parse_obj_as(IPFSGatewayResponse, obj=raw_response.json())
    except Exception as e:
        raise ConnectionError(f"Can't push file to IPFS Gateway: {e}")
    return parsed_response
