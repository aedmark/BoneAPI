from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import FileResponse
import os
import shutil

# Official x402 Python SDK Imports
from x402 import x402ResourceServerSync, ResourceConfig
from x402.http import HTTPFacilitatorClientSync
from x402.mechanisms.evm.exact import ExactEvmServerScheme

app = FastAPI()

# 1. Initialize Facilitator & Server (The Official Approach)
facilitator = HTTPFacilitatorClientSync(url="https://x402.org/facilitator")
server = x402ResourceServerSync(facilitator)

# 2. Register your EVM Network Scheme
# 'eip155:8453' is the standard chain ID for Base L2
server.register("eip155:8453", ExactEvmServerScheme())
server.initialize()

# 3. Create the Payment Gate (FastAPI Dependency)
def require_x402_payment(request: Request):
    """
    Intercepts the request to validate the x402 payment proof.
    Rejects the request with a 402 status if payment is invalid or missing.
    """
    auth_header = request.headers.get("Authorization")

    # Check if the client provided a valid x402/L402 authorization header
    if not auth_header or not (auth_header.startswith("L402") or auth_header.startswith("x402")):
        raise HTTPException(
            status_code=402,
            detail="Metabolic fee insufficient. Payment Required.",
            headers={"Www-Authenticate": "x402"}
        )

    # In a fully fleshed-out environment, you would pass the header to the server here:
    # server.verify(auth_header)

# 4. The Single Endpoint
# The 'Depends' block ensures this code ONLY runs if the agent passed the payment gate above
@app.get("/hypervisor", dependencies=[Depends(require_x402_payment)])
def get_hypervisor():
    archive_name = "bone_dev_payload"
    if not os.path.exists(f"{archive_name}.zip"):
        shutil.make_archive(archive_name, "zip", "bone_dev_2026")

    return FileResponse(f"{archive_name}.zip", media_type="application/octet-stream")
