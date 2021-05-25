from django import forms
from django.utils.translation import ugettext_lazy as _

from snapboard.models import Category, Thread, Post, WatchList
from snapboard.utils import RequestForm, RequestModelForm


__all__ = ["PostForm", "ThreadForm", "ThreadEditForm"]

Textarea = lambda cols: forms.Textarea(attrs={'rows':'8', 'cols': str(cols)})


class PostForm(RequestModelForm):
    """ For editing posts. """
    text = forms.CharField(label='', widget=Textarea('90'))
          
    class Meta:
        model = Post
        fields = ("text",)
    
    def save(self, thread=None):
        data = self.cleaned_data
        ip = self.request.META.get("REMOTE_ADDR")

        # TODO: Make this less stupid.

        # Editing an existing post.
        if self.instance.id is not None:
            self.instance.text = data["text"]
            self.instance.ip = ip
            self.instance.save()
            return self.instance
        # Working on a new post.
        else:
            user = self.request.user
            return Post.objects.create_and_notify(thread, user, text=data["text"], ip=ip)

""" When I inherited this code, for some reason the Thread form doesn't use its model Meta. This 
may be because of the slightly strange saving process it needs to do for thread+post, but 
perhaps could be refactored to make that simpler. """

class ThreadForm(RequestForm):
    """ This form is for creating new threads, but needs to save the first post as well."""
    subject = forms.CharField(max_length=80, label='Subject', widget=forms.TextInput(attrs={'size':'50'}))
    post = forms.CharField(label='Post', widget=Textarea(80))
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    def __init__(self, *args, **kwargs):
        u=kwargs['request'].user
        super(ThreadForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset=Category.objects.get_user_post_cats(u)
       
    
    def save(self):
        data = self.cleaned_data
        user = self.request.user
        priv = False
        if not user.has_perm('snapboard.post_unmoderated'): # moderated users check for thread creation.
          priv=True
        thread = Thread.objects.create_thread(**{
            "user": user,
            "category": data['category'],
            "name": data['subject'],
            "private": priv,
            "last_poster": user
        })
        
        ip = self.request.META.get("REMOTE_ADDR")
        Post.objects.create_and_notify(thread, user, text=data['post'], ip=ip)
        return thread


class ThreadEditForm(RequestModelForm):
    """ This form is used to edit the first post in the thread, so must allow editing of post text as well as subject and category."""
    name = forms.CharField(max_length=80, label='Subject', widget=forms.TextInput(attrs={'size':'50'})) 
    post = forms.CharField(label=_('Post'), widget=Textarea(90))
    post_pk = forms.CharField(widget=forms.HiddenInput())
    category = forms.ModelChoiceField(queryset=Category.objects.none(), empty_label=None)
    # user categories not available at declaration time, so pass an empty query set.

    def __init__(self, *args, **kwargs):
      #remove our extra kwarg and add the value to 'initial' before calling parent class's save method.
      p=kwargs.pop('thepost', None)
      u=kwargs['request'].user
      initial={}
      if p:
         initial['post']=p.text
         initial['post_pk']=p.id      
      super(ThreadEditForm, self).__init__(initial=initial, *args, **kwargs)
      #update the category choices with those available to this user
      self.fields['category'].queryset=Category.objects.get_user_post_cats(u)

    class Meta:
      model = Thread
      fields = ('name', 'post', 'category', 'post_pk')
    
      
    def save(self):
      data = self.cleaned_data
      p = Post.objects.get(pk=data['post_pk'])
      p.text = data['post']
      p.save()
      super(ThreadEditForm, self).save()
      
      
      
      

  