import uuid
from .mock_model import BackModel, Field

"""Some basic model classes - the only import reason to subclass BackModel at
the moment is to get the post_save and post_delete signal handling"""

class ChatUser(BackModel):
    """User class"""

    meta = {
        'sync_name' : 'User',
    }

    id         = Field(default=lambda:str(uuid.uuid4()))
    screenName = Field(default='Anonymous')

class ChatMessage(BackModel):
    """Message"""

    id         = Field(default=lambda:str(uuid.uuid4()))
    userId     = Field()
    message    = Field(default='')
    color      = Field(default='black')
    screenName = Field(default='anonymous')

    # TODO - need to override the save method to cap the collection size...

#
#  A few default messages
#
ChatMessage(message="message one").save()
ChatMessage(message="message two").save()
ChatMessage(message="message three").save()
