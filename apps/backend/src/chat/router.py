"""Chat HTTP routes — sessions, messages, SSE stream."""

from __future__ import annotations

from collections.abc import Iterator

from backend_shared.schemas import ApiResponse
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.chat.rate_limit import get_chat_rate_limiter
from src.chat.schemas import (
    ChatSessionResponse,
    CreateSessionRequest,
    MessageListResponse,
    MessageResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from src.chat.service import (
    create_session,
    delete_session,
    get_session_by_public_id,
    list_messages,
    message_to_dict,
    post_message,
    session_to_response_dict,
    stream_reply_chunks,
    touch_session,
)
from src.settings import get_settings

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/status")
def chat_module_status() -> dict[str, str]:
    """Lightweight marker that the chat module router is mounted."""
    return {"module": "chat", "status": "ready"}


@router.post("/sessions", response_model=ApiResponse[ChatSessionResponse], status_code=201)
def create_chat_session(
    body: CreateSessionRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ApiResponse[ChatSessionResponse]:
    """Create an anonymous visitor session for an owner's digital twin."""
    ip = body.visitor_ip
    if not ip and request.client:
        ip = request.client.host
    session = create_session(db, owner_id=body.owner_id, visitor_ip=ip)
    # Reload with relationships for response enrichment.
    session = get_session_by_public_id(db, session.public_id)
    return ApiResponse.ok(ChatSessionResponse.model_validate(session_to_response_dict(session)))


@router.get("/sessions/{session_id}", response_model=ApiResponse[ChatSessionResponse])
def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[ChatSessionResponse]:
    """Return session metadata (rejects expired sessions)."""
    session = get_session_by_public_id(db, session_id)
    return ApiResponse.ok(ChatSessionResponse.model_validate(session_to_response_dict(session)))


@router.delete("/sessions/{session_id}", response_model=ApiResponse[dict[str, str]])
def end_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[dict[str, str]]:
    """Visitor ends the chat session."""
    delete_session(db, session_id)
    return ApiResponse.ok({"session_id": session_id, "status": "deleted"})


@router.get(
    "/sessions/{session_id}/messages",
    response_model=ApiResponse[MessageListResponse],
)
def get_messages(
    session_id: str,
    db: Session = Depends(get_db),
) -> ApiResponse[MessageListResponse]:
    """Return message history for a session."""
    get_chat_rate_limiter().assert_allowed(session_id)
    messages = list_messages(db, session_id)
    return ApiResponse.ok(
        MessageListResponse(
            session_id=session_id,
            messages=[MessageResponse.model_validate(message_to_dict(m)) for m in messages],
        )
    )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ApiResponse[SendMessageResponse],
)
def send_message(
    session_id: str,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[SendMessageResponse]:
    """Send a visitor message and receive a synchronous AI reply."""
    get_chat_rate_limiter().assert_allowed(session_id)
    result = post_message(db, session_id, body.content)
    session = result["session"]
    return ApiResponse.ok(
        SendMessageResponse(
            visitor_message=MessageResponse.model_validate(
                message_to_dict(result["visitor_message"])
            ),
            reply=MessageResponse.model_validate(message_to_dict(result["reply"])),
            session_id=session.public_id,
            expires_at=session.expires_at,
            boundary_redirect=bool(result["boundary_redirect"]),
        )
    )


def _sse_format(event: str, data: str) -> str:
    # Escape newlines in data for SSE multi-line fields.
    lines = data.split("\n")
    payload = "\n".join(f"data: {line}" for line in lines)
    return f"event: {event}\n{payload}\n\n"


@router.get("/sse/{session_id}/stream")
def stream_message_sse(
    session_id: str,
    content: str,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """SSE stream: generate a reply for ``content`` and emit text chunks.

    Query param ``content`` holds the visitor message (max 10K). Clients may
    also use the synchronous POST endpoint; WebSocket is deferred post-MVP.
    """
    get_chat_rate_limiter().assert_allowed(session_id)
    # Generate full reply first (MVP), then stream chunks for UX.
    result = post_message(db, session_id, content)
    reply_text = result["reply"].content
    boundary = bool(result["boundary_redirect"])
    settings = get_settings()
    chunks = stream_reply_chunks(reply_text, chunk_size=settings.chat_sse_chunk_size)

    def event_iter() -> Iterator[str]:
        yield _sse_format("meta", f'{{"boundary_redirect": {str(boundary).lower()}}}')
        for chunk in chunks:
            yield _sse_format("token", chunk)
        yield _sse_format("done", '{"status":"completed"}')

    return StreamingResponse(event_iter(), media_type="text/event-stream")


@router.post("/sse/{session_id}/stream")
def stream_message_sse_post(
    session_id: str,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """SSE stream via POST body (preferred over long query strings)."""
    get_chat_rate_limiter().assert_allowed(session_id)
    result = post_message(db, session_id, body.content)
    reply_text = result["reply"].content
    boundary = bool(result["boundary_redirect"])
    settings = get_settings()
    chunks = stream_reply_chunks(reply_text, chunk_size=settings.chat_sse_chunk_size)
    # Keep session touched (already done in post_message).
    _ = touch_session

    def event_iter() -> Iterator[str]:
        yield _sse_format("meta", f'{{"boundary_redirect": {str(boundary).lower()}}}')
        for chunk in chunks:
            yield _sse_format("token", chunk)
        yield _sse_format("done", '{"status":"completed"}')

    return StreamingResponse(event_iter(), media_type="text/event-stream")
