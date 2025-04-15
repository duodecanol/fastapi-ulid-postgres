import json
import uuid
from typing import Dict

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import Character
from app.models.chat import ChatMessage, ChatSession
from app.models.user import User


@pytest.mark.asyncio
async def test_read_sessions(
    client: AsyncClient, token_headers: Dict[str, str], test_chat_session: ChatSession
):
    """Test retrieving chat sessions."""
    response = await client.get("/api/v1/chat/sessions", headers=token_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check if the test session is in the response
    session_ids = [session["id"] for session in data]
    assert str(test_chat_session.id) in session_ids


@pytest.mark.asyncio
async def test_read_sessions_by_character(
    client: AsyncClient,
    token_headers: Dict[str, str],
    test_chat_session: ChatSession,
    test_character: Character,
):
    """Test retrieving chat sessions filtered by character."""
    response = await client.get(
        f"/api/v1/chat/sessions?character_id={test_character.id}", headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check if all sessions are for the specified character
    for session in data:
        assert session["character_id"] == str(test_character.id)


@pytest.mark.asyncio
async def test_create_session(
    client: AsyncClient, token_headers: Dict[str, str], test_character: Character
):
    """Test creating a new chat session."""
    session_data = {
        "character_id": str(test_character.id),
        "session_type": "dialogue",
        "intimacy_level": 2,
        "plot": "Test plot for the session",
    }

    response = await client.post(
        "/api/v1/chat/sessions", headers=token_headers, json=session_data
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["character_id"] == str(test_character.id)
    assert data["session_type"] == "dialogue"
    assert data["intimacy_level"] == 2
    assert data["plot"] == "Test plot for the session"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_read_session(
    client: AsyncClient, token_headers: Dict[str, str], test_chat_session: ChatSession
):
    """Test retrieving a specific chat session by ID."""
    response = await client.get(
        f"/api/v1/chat/sessions/{test_chat_session.id}", headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == str(test_chat_session.id)
    assert data["user_id"] == str(test_chat_session.user_id)
    assert data["character_id"] == str(test_chat_session.character_id)
    assert data["session_type"] == test_chat_session.session_type


@pytest.mark.asyncio
async def test_update_session(
    client: AsyncClient, token_headers: Dict[str, str], test_chat_session: ChatSession
):
    """Test updating a chat session."""
    update_data = {"intimacy_level": 3, "plot": "Updated test plot"}

    response = await client.put(
        f"/api/v1/chat/sessions/{test_chat_session.id}",
        headers=token_headers,
        json=update_data,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == str(test_chat_session.id)
    assert data["intimacy_level"] == 3
    assert data["plot"] == "Updated test plot"


@pytest.mark.asyncio
async def test_delete_session(
    client: AsyncClient,
    token_headers: Dict[str, str],
    test_chat_session: ChatSession,
    dbsession: AsyncSession,
):
    """Test deleting a chat session."""
    response = await client.delete(
        f"/api/v1/chat/sessions/{test_chat_session.id}", headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify the session was deleted
    result = await dbsession.get(ChatSession, test_chat_session.id)
    assert result is None


@pytest.mark.asyncio
async def test_read_messages(
    client: AsyncClient,
    token_headers: Dict[str, str],
    test_chat_session: ChatSession,
    test_chat_message: ChatMessage,
):
    """Test retrieving messages for a chat session."""
    response = await client.get(
        f"/api/v1/chat/sessions/{test_chat_session.id}/messages", headers=token_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check if the test message is in the response
    message_ids = [message["id"] for message in data]
    assert str(test_chat_message.id) in message_ids


@pytest.mark.asyncio
async def test_create_message(
    client: AsyncClient, token_headers: Dict[str, str], test_chat_session: ChatSession
):
    """Test creating a new chat message."""
    message_data = {
        "type": "user",
        "content": "This is a new test message",
        "chat_session_id": str(test_chat_session.id),
    }

    response = await client.post(
        f"/api/v1/chat/sessions/{test_chat_session.id}/messages",
        headers=token_headers,
        json=message_data,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["type"] == "user"
    assert data["content"] == "This is a new test message"
    assert data["chat_session_id"] == str(test_chat_session.id)
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test that endpoints require authentication."""
    # Try to access sessions without token
    response = await client.get("/api/v1/chat/sessions")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Try to create a session without token
    session_data = {
        "character_id": str(uuid.uuid4()),
        "session_type": "dialogue",
        "intimacy_level": 1,
    }
    response = await client.post("/api/v1/chat/sessions", json=session_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_session_not_found(client: AsyncClient, token_headers: Dict[str, str]):
    """Test handling of non-existent session."""
    non_existent_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/chat/sessions/{non_existent_id}", headers=token_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Chat session not found"


@pytest.mark.asyncio
async def test_invalid_character_id(client: AsyncClient, token_headers: Dict[str, str]):
    """Test validation of character ID when creating a session."""
    session_data = {
        "character_id": str(uuid.uuid4()),  # Non-existent character ID
        "session_type": "dialogue",
        "intimacy_level": 1,
    }

    response = await client.post(
        "/api/v1/chat/sessions", headers=token_headers, json=session_data
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Character not found"
