from django.urls import path
from .views import MessageListCreateView, MessageReplyCreateView
urlpatterns=[path("messages/",MessageListCreateView.as_view()),path("messages/<uuid:pk>/replies/",MessageReplyCreateView.as_view())]
