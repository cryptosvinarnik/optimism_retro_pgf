import asyncio

from loguru import logger
from web3.contract import Contract

from retro_pgf.const import ABI, DECENT_CONTRACT, NFT_CONTRACT, RPC
from retro_pgf.mint import RetroPGF, get_web3, load_contract
from retro_pgf.utils import init_logger


async def worker(
    q: asyncio.Queue,
    decent_contract: Contract,
    nft_contract: Contract,
    is_free_mint: bool
) -> None:
    while not q.empty():
        private_key = await q.get()

        try:
            retro_pgf = RetroPGF(get_web3(RPC), private_key)

            logger.info(f"[{retro_pgf.account.address}] Trying to mint NFT.")

            if is_free_mint:
                tx_hash = await retro_pgf.free_mint(nft_contract)
            else:
                tx_hash = await retro_pgf.mint(decent_contract)

            logger.success(f"[{retro_pgf.account.address}] Sent mint TX with hash {tx_hash.hex()}")

        except Exception as e:
            logger.error(f"[{retro_pgf.account.address}] Failed with error: {e}")


async def main():
    init_logger()

    decent_contract = load_contract(ABI, DECENT_CONTRACT)
    nft_contract = load_contract(ABI, NFT_CONTRACT)

    with open("accounts.txt", "r") as f:
        accounts = f.read().splitlines()

    logger.info(f"Loaded {len(accounts)=}")

    is_bridge = input("Mint for free? (n/n): ").lower() == "y"

    q = asyncio.Queue()
    for account in accounts:
        q.put_nowait(account)

    workers = [
        asyncio.create_task(worker(q, decent_contract, nft_contract, is_bridge))
        for _ in range(5)
    ]

    await asyncio.gather(*workers)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Exiting...")
