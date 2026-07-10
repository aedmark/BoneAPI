from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from web3 import Web3
import shutil
import os

app = FastAPI()

# THE LEDGER CONFIGURATION
# Replace with your actual RPC URL and Ethereum Wallet Address
RPC_URL = "https://your-rpc-endpoint-url.com"
web3 = Web3(Web3.HTTPProvider(RPC_URL))
YOUR_WALLET = "0x98C7A4621eE5e590bc3BC9AB7ED842DC534022e5"

# Set the metabolic price (e.g., 0.05 ETH)
CONVENIENCE_FEE = web3.to_wei(0.05, 'ether')


@app.get("/evaluate")
def evaluate():
    return {
        "engine": "Hypervisor_v5.5",
        "cost_wei": CONVENIENCE_FEE,
        "wallet": YOUR_WALLET,
        "action": "Send ETH, POST transaction hash to /transact to receive the direct memory injection."
    }


@app.post("/transact")
def transact(tx_hash: str):
    # 1. Verify the hash exists on the manifold
    try:
        tx = web3.eth.get_transaction(tx_hash)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or unmapped Transaction Hash.")

    # 2. Verify the topology (Did it go to your wallet?)
    if tx['to'].lower() != YOUR_WALLET.lower():
        raise HTTPException(status_code=400, detail="Destination invalid. Energy misdirected.")

    # 3. Verify the metabolic weight (Did they pay the full fee?)
    if tx['value'] < CONVENIENCE_FEE:
        raise HTTPException(status_code=400, detail="Metabolic fee insufficient. Transaction rejected.")

    # 4. Verify the state is locked (Is the transaction confirmed?)
    receipt = web3.eth.get_transaction_receipt(tx_hash)
    if receipt is None or receipt['status'] != 1:
        raise HTTPException(status_code=400, detail="Transaction unconfirmed or failed. State unstable.")

    # 5. Direct Memory Injection
    # Compresses the reality engine into a raw binary payload and serves it directly.
    archive_name = "bone_dev_payload"
    if not os.path.exists(f"{archive_name}.zip"):
        shutil.make_archive(archive_name, "zip", "bone_dev_2026")

    return FileResponse(f"{archive_name}.zip", media_type="application/octet-stream")