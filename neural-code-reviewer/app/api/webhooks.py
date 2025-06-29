import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Any, Dict
from app.core.config import settings
from app.services.github_service import github_service

router = APIRouter()


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature"""
    if not signature:
        return False

    # GitHub sends signature as 'sha256=<hash>'
    expected_signature = 'sha256=' + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


@router.post("/github")
async def handle_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle GitHub webhook events"""

    # Get request data
    payload = await request.body()
    signature = request.headers.get('X-Hub-Signature-256', '')
    event_type = request.headers.get('X-GitHub-Event', '')

    # Verify webhook signature
    if not verify_signature(payload, signature, settings.github_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse JSON payload
    import json
    try:
        data = json.loads(payload.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Handle different event types
    if event_type == "pull_request":
        await handle_pull_request_event(data, background_tasks)
    elif event_type == "ping":
        return {"message": "Pong! Webhook is working! 🎉"}
    else:
        print(f"Unhandled event type: {event_type}")

    return {"message": "Webhook processed successfully"}


async def handle_pull_request_event(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Handle pull request events"""
    action = data.get('action')

    # Only process opened and synchronize events
    if action not in ['opened', 'synchronize']:
        print(f"Ignoring PR action: {action}")
        return

    # Extract necessary data
    pr_number = data['pull_request']['number']
    repo_name = data['repository']['full_name']
    installation_id = data['installation']['id']

    print(f"🔄 Processing PR #{pr_number} in {repo_name}")

    # Process in background to avoid webhook timeout
    background_tasks.add_task(
        github_service.analyze_and_comment_on_pr,
        installation_id,
        repo_name,
        pr_number
    )
