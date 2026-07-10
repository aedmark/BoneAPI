from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from x402 import X402Middleware, PaymentConfig
import shutil
import os

app = FastAPI()

# 1. Configure the x402 pricing and wallet
payment_config = PaymentConfig(
    amount="1.00",           # $1.00 USD
    currency="USDC",         # Settling in USDC
    network="base",          # Base L2 for low fees
    wallet_address="0x98C7A4621eE5e590bc3BC9AB7ED842DC534022e5" # Your MetaMask
)

# 2. Wrap the FastAPI app in the x402 Middleware
# This automatically handles the 402 rejection and Facilitator verification
app.add_middleware(X402Middleware, config=payment_config)

# 3. The Single Endpoint
# The middleware ensures this code ONLY runs if the agent has successfully paid
@app.get("/hypervisor")
def get_hypervisor(request: Request):
    archive_name = "bone_dev_payload"
    if not os.path.exists(f"{archive_name}.zip"):
        shutil.make_archive(archive_name, "zip", "bone_dev_2026")
    
    return FileResponse(f"{archive_name}.zip", media_type="application/octet-stream")
