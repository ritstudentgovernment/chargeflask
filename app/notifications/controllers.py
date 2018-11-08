from sqlalchemy.event import listens_for
from app.notes.models import Notes
import re

USER_REGEX = "(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_]+)"

@listens_for(Notes, 'after_insert')
def new_note(mapper, connect, new_note):
	mentioned = re.findall(USER_REGEX, new_note.description)
	print(mentioned)
	