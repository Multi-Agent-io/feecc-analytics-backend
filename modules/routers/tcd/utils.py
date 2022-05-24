import typing as tp

import httpx
import os
import json
from loguru import logger
from pydantic import parse_obj_as
from robonomicsinterface import RobonomicsInterface
from modules.database import MongoDbWrapper

from modules.routers.tcd.models import IPFSGatewayResponse, ProtocolData


IPFS_GATEWAY_HOST = os.getenv("IPFS_GATEWAY_HOST")


async def convert_protocol(protocol: ProtocolData, exclude_fields: tp.Set[str] = set()) -> bytes:
    return json.dumps(protocol.dict(exclude=exclude_fields), default=str).encode("utf-8")


async def post_to_datalog(content: str) -> str:
    """echo provided string to the Robonomics datalog"""
    logger.info(f"Posting data '{content}' to Robonomics datalog")
    txn_hash: str = RobonomicsInterface(seed=os.getenv("ROBONOMICS_SEED")).record_datalog(content)
    logger.info(f"Data '{content}' has been posted to the Robonomics datalog. {txn_hash=}")
    return txn_hash


async def post_ipfs_cid_to_datalog(internal_id: str, ipfs_cid: str) -> None:
    """Post protocol to datalog and record TXN Hash + IPFS cid to database"""
    txn_hash = await post_to_datalog(content=ipfs_cid)
    await MongoDbWrapper().append_hashes_to_protocol(internal_id=internal_id, ipfs_cid=ipfs_cid, txn_hash=txn_hash)


async def push_to_ipfs_gateway(protocol: ProtocolData, username: str) -> IPFSGatewayResponse:
    """Push protocol to IPFS Gateway, returns IPFS Hash and Robonomics substrate TXN Hash"""
    logger.info(f"Pushing protocol {protocol.protocol_id} to IPFS and Robonomics datalog")
    protocol_raw = {
        "file_data": (
            f"protocol-{protocol.protocol_id}.json",
            await convert_protocol(protocol=protocol, exclude_fields={"txn_hash", "ipfs_cid"}),
        )
    }
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
