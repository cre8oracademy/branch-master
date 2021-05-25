from django import forms

from userena.contrib.umessages.fields import CommaSeparatedUserField
from userena.contrib.umessages.models import Message, MessageRecipient

class PmComposeForm(forms.Form):
  to = CommaSeparatedUserField(label="To",
                          widget=forms.TextInput())
  body = forms.CharField(label="Message",
                         widget=forms.Textarea({'class': 'message', 'rows': 5}),
                         required=True)

  def save(self, sender):
      """
      Save the message and send it out into the wide world.

      :param sender:
          The :class:`User` that sends the message.

      :param parent_msg:
          The :class:`Message` that preceded this message in the thread.

      :return: The saved :class:`Message`.

      """
      to_user_list = self.cleaned_data['to']
      body = self.cleaned_data['body']

      msg = Message.objects.send_message(sender,
                                         to_user_list,
                                         body)

      return msg
  