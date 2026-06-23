"""
Shared constants: ConversationHandler states, inline-button callback_data
values, and the keys used inside context.user_data.
"""

# --- Conversation states -------------------------------------------------
STATE_SPEAKER_ID = 0
STATE_CONFIRM_ID = 1
STATE_CONSENT = 2
STATE_RECORDING = 3
STATE_REVIEW = 4

# --- Callback data (inline button payloads) ------------------------------
CB_CONFIRM_YES = "confirm_yes"
CB_CONFIRM_NO = "confirm_no"
CB_CONSENT_YES = "consent_yes"
CB_CONSENT_NO = "consent_no"
CB_SUBMIT = "submit"
CB_REDO = "redo"
CB_DELETE = "delete"

# --- context.user_data keys ----------------------------------------------
UD_SPEAKER_ID = "speaker_id"
UD_PARTICIPANT = "participant"
UD_CURRENT_SENTENCE = "current_sentence"
UD_TEMP_AUDIO_PATH = "temp_audio_path"
