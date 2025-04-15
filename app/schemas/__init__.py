# Import all schemas in alphabetical order
from app.schemas.character import Character, CharacterCreate, CharacterUpdate

__all__ = [
    # Character schemas
    "Character",
    "CharacterCreate",
    "CharacterUpdate",
    # Chat schemas
    "ChatMessage",
    "ChatMessageCreate",
    "ChatMessageLanggraph",
    "ChatMessageUpdate",
    "ChatSession",
    "ChatSessionCreate",
    "ChatSessionInfoDialogue",
    "ChatSessionInfoStory",
    "ChatSessionUpdate",
    "LanggraphDialogueRequest",
    "LanggraphStoryRequest",
    # Settings schemas
    "SettingsInstance",
    "SettingsInstanceCreate",
    "SettingsInstanceUpdate",
    "SettingsItemSpec",
    "SettingsItemSpecCreate",
    "SettingsItemSpecUpdate",
    "SettingsTemplate",
    "SettingsTemplateCreate",
    "SettingsTemplateUpdate",
    "SettingsValue",
    "SettingsValueCreate",
    "SettingsValueUpdate",
    "SettingsValuesUpdate",
    # User schemas
    "LoginForm",
    "Token",
    "TokenPayload",
    "User",
    "UserCreate",
    "UserInDBBase",
    "UserPersona",
    "UserPersonaCreate",
    "UserPersonaUpdate",
    "UserUpdate",
    "UserWithPassword",
]
