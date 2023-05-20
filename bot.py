import asyncio
import json
import random
import time

from config import WALLETS
from web3 import AsyncWeb3
from web3.providers.async_rpc import AsyncHTTPProvider


polygon_rpc = "https://polygon-rpc.com"
polygon_w3 = AsyncWeb3(AsyncHTTPProvider(polygon_rpc))

rarible_abi = json.load(open('rarible_abi.json'))
rarible_address = polygon_w3.to_checksum_address('0x8E0DCCa4E6587d2028ed948b7285791269059a62')
rarible_contract = polygon_w3.eth.contract(address=rarible_address, abi=rarible_abi)

async def check_status(wallet, claim_txn_hash):
    account = polygon_w3.eth.account.from_key(wallet)
    address = account.address

    print(f'Wallet: {address} | In progress...')
    while True:
        try:
            status = await polygon_w3.eth.get_transaction_receipt(claim_txn_hash)
            i = status['status']
            if i >= 0:
                return i
            time.sleep(5)
        except Exception as error:
            time.sleep(5)
            

async def claim_nft(wallet: str):
    account = polygon_w3.eth.account.from_key(wallet)
    address = account.address

    polygon_transaction_info = {
        "receiver": address,
        "quantity": 1,
        "currency": '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
        "price": 0,
        "proof": (['0x0000000000000000000000000000000000000000000000000000000000000000'], 1, 0, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'),
        "data": '0x'
    }

    delay = random.randint(1, 1000)
    print(f'Wallet: {address} | Bot will wait for {delay} seconds before the start.')
    await asyncio.sleep(delay)
    claim_txn = await rarible_contract.functions.claim(
        polygon_transaction_info["receiver"],
        polygon_transaction_info["quantity"],
        polygon_transaction_info["currency"],
        polygon_transaction_info["price"],
        polygon_transaction_info["proof"],
        polygon_transaction_info["data"]
    ).build_transaction(
        {
            'from': address,
            'value': 0,
            'gas': 200000,
            'gasPrice': await polygon_w3.eth.gas_price,
            'nonce': await polygon_w3.eth.get_transaction_count(address)
        }
    )
    signed_claim_txn = account.sign_transaction(claim_txn)
    claim_txn_hash = await polygon_w3.eth.send_raw_transaction(signed_claim_txn.rawTransaction)
    status = await check_status(wallet, claim_txn_hash)

    if status == 1:
        print(
            f"Successfuly minted | {address} | Transaction: https://polygonscan.com/tx/{polygon_w3.to_hex(claim_txn_hash)}")
    elif status == 0:
        print(f'{address}: error cuz u have already minted (most likely)')


async def main():
    tasks = []
    for wallet in WALLETS:
        task = claim_nft(wallet)
        tasks.append(task)
    await asyncio.sleep(2)
    mints = await asyncio.gather(*tasks)
    print("FINISHED")

if __name__ == '__main__':
    asyncio.run(main())
