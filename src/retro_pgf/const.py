RPC = "https://rpc.ankr.com/optimism"

NFT_CONTRACT = "0xd89dBBd35C24E07C7727BF1eF36cd1F02aEA158E"
DECENT_CONTRACT = "0xcA11bde05977b3631167028862bE2a173976CA11"

# 0.00044 ETH
DECENT_MINT_PRICE = 440000000000000


ABI = [
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "target",
                        "type": "address"
                    },
                    {
                        "internalType": "bool",
                        "name": "allowFailure",
                        "type": "bool"
                    },
                    {
                        "internalType": "uint256",
                        "name": "value",
                        "type": "uint256"
                    },
                    {
                        "internalType": "bytes",
                        "name": "callData",
                        "type": "bytes"
                    }
                ],
                "internalType": "struct Multicall3.Call3Value[]",
                "name": "calls",
                "type": "tuple[]"
            }
        ],
        "name": "aggregate3Value",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "bool",
                        "name": "success",
                        "type": "bool"
                    },
                    {
                        "internalType": "bytes",
                        "name": "returnData",
                        "type": "bytes"
                    }
                ],
                "internalType": "struct Multicall3.Result[]",
                "name": "returnData",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "numberOfTokens",
                "type": "uint256"
            }
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]
