from django.test import TestCase
import json

from .models import Conversation

# Create your tests here.
class ConversationModelTest(TestCase):
    def test_conversation(self):
        conversation = Conversation(imposter_id='0',
                                    fan_id='1',
                                    imposter_page='10',
                                    fan_page='11',
                                    content=json.dumps({
                                            '0': 'hello',
                                            '1': 'hello, too'
                                        })
                                    )
        conversation.save()
        obj = Conversation.objects.get(imposter_id='0')
        assert obj 
        obj.delete()
        try:
            Conversation.objects.get(imposter_id='0')
            assert(False)
        except:
            pass


