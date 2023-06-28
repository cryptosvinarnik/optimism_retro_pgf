from eth_account import Account
from loguru import logger
from web3 import Web3
from web3.contract import Contract
from web3.eth import AsyncEth
from web3.exceptions import ContractLogicError
from web3.types import HexBytes, TxParams

from retro_pgf.const import DECENT_MINT_PRICE, NFT_CONTRACT


def load_contract(abi: dict, address: str) -> Contract:
    return Web3().eth.contract(address=address, abi=abi)


def get_web3(rpc_url: str) -> Web3:
    return Web3(
        Web3.AsyncHTTPProvider(
            rpc_url,
        ),
        middlewares=[],
        modules={"eth": (AsyncEth,)}
    )


class Web3Wrapper:
    def __init__(self, web3: Web3, private_key: str) -> None:
        self.web3 = web3
        self.account = Account.from_key(private_key)

    async def estimate_and_send_transaction(
        self,
        tx_params: TxParams,
        gas_buffer: int = 1.05
    ) -> HexBytes:
        """Estimate gas, add a buffer, and send a transaction"""

        for _ in range(3):
            try:
                estimated_gas = await self.web3.eth.estimate_gas(tx_params)
                break
            except ContractLogicError as e:
                # If the estimate fails, try again for up to 3 times
                logger.error(f"Failed to estimate gas for {tx_params=} with error: {e}")
                continue
        else:
            # If the estimate fails for 3 times, raise the error
            raise ContractLogicError("Failed to estimate gas for transaction")

        if (
            ("gas" not in tx_params) or
            (tx_params["gas"] is None) or
            (tx_params["gas"] < estimated_gas)
        ):
            tx_params["gas"] = tx_params["gas"] = int(estimated_gas * gas_buffer)

        signed_tx = self.account.sign_transaction(tx_params)

        return await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    @property
    async def eip_1559_gas(self) -> dict:
        base_fee = await self.web3.eth.gas_price

        max_priority_fee = await self.web3.eth.max_priority_fee

        return {
            "maxFeePerGas": max_priority_fee + base_fee * 2, 
            "maxPriorityFeePerGas": max_priority_fee
        }


class RetroPGF(Web3Wrapper):
    def __init__(self, web3: Web3, private_key: str) -> None:
        super().__init__(web3, private_key)

    def free_mint_data(self, nft_contract: Contract) -> str:
        return nft_contract.functions.mint(
            to=self.account.address,
            numberOfTokens=1
        )._encode_transaction_data()

    async def free_mint(self, nft_contract: Contract) -> HexBytes:
        data = self.free_mint_data(nft_contract)

        return await self.estimate_and_send_transaction({
            "chainId": await self.web3.eth.chain_id,
            "nonce": await self.web3.eth.get_transaction_count(self.account.address, "pending"),
            "from": self.account.address,
            "to": nft_contract.address,
            "data": data,
            "value": 0,
            **(await self.eip_1559_gas)
        })
    
    async def mint(self, decent_contract: Contract) -> HexBytes:
        data_object = [
            (
                NFT_CONTRACT,
                False,
                0,
                self.free_mint_data(decent_contract),
            ),
            (
                '0xAcCC1fe6537eb8EB56b31CcFC48Eb9363e8dd32E',
                False,
                DECENT_MINT_PRICE,
                b"",
            )
        ]

        data = decent_contract.functions.aggregate3Value(data_object)._encode_transaction_data()

        return await self.estimate_and_send_transaction({
            "chainId": await self.web3.eth.chain_id,
            "nonce": await self.web3.eth.get_transaction_count(self.account.address, "pending"),
            "from": self.account.address,
            "to": decent_contract.address,
            "data": data,
            "value": DECENT_MINT_PRICE,
            **(await self.eip_1559_gas)
        })
