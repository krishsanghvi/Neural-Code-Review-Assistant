import hmac
import hashlib
import json
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Any, Dict
from app.core.config import settings
from app.services.github_service import github_service

router = APIRouter()


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature"""
    if not signature:
        print("❌ No signature provided")
        return False

    # GitHub sends signature as 'sha256=<hash>'
    expected_signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    is_valid = hmac.compare_digest(expected_signature, signature)
    print(f"🔐 Signature valid: {is_valid}")
    return is_valid


@router.post("/github")
async def handle_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle GitHub webhook events"""

    print("🚨 WEBHOOK RECEIVED!")
    print("=" * 50)

    # Get request data
    payload = await request.body()
    signature = request.headers.get('X-Hub-Signature-256', '')
    event_type = request.headers.get('X-GitHub-Event', '')
    delivery_id = request.headers.get('X-GitHub-Delivery', '')

    print(f"📡 Event Type: {event_type}")
    print(f"🆔 Delivery ID: {delivery_id}")
    print(f"📏 Payload Size: {len(payload)} bytes")
    print(f"🔑 Has Signature: {'Yes' if signature else 'No'}")
    print(
        f"🔒 Webhook Secret Set: {'Yes' if settings.github_webhook_secret else 'No'}")

    # Skip signature verification for debugging (REMOVE THIS LATER!)
    if not settings.github_webhook_secret:
        print("⚠️  WARNING: No webhook secret set - skipping signature verification")
    elif not verify_signature(payload, signature, settings.github_webhook_secret):
        print("❌ Signature verification failed")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    try:
        data = json.loads(payload.decode('utf-8'))
        print(f"✅ JSON parsed successfully")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Print some key info from payload
    if 'repository' in data:
        print(f"📁 Repository: {data['repository']['full_name']}")
    if 'pull_request' in data:
        print(f"🔀 PR Number: {data['pull_request']['number']}")
        print(f"🎯 PR Action: {data['action']}")

    # Handle different event types
    if event_type == "pull_request":
        print("🔄 Processing pull request event...")
        await handle_pull_request_event(data, background_tasks)
    elif event_type == "ping":
        print("🏓 Ping event received")
        return {"message": "Pong! Webhook is working! 🎉"}
    else:
        print(f"❓ Unhandled event type: {event_type}")

    print("=" * 50)
    return {"message": "Webhook processed successfully"}


async def handle_pull_request_event(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Handle pull request events"""
    action = data.get('action')

    print(f"🎬 PR Action: {action}")

    # Only process opened and synchronize events
    if action not in ['opened', 'synchronize']:
        print(f"⏭️  Ignoring PR action: {action}")
        return

    # Extract necessary data
    pr_number = data['pull_request']['number']
    repo_name = data['repository']['full_name']
    installation_id = data['installation']['id']

    print(f"🔄 Processing PR #{pr_number} in {repo_name}")
    print(f"🏗️  Installation ID: {installation_id}")

    # Process in background to avoid webhook timeout
    background_tasks.add_task(
        github_service.analyze_and_comment_on_pr,
        installation_id,
        repo_name,
        pr_number
    )

    print("✅ Background task queued")
