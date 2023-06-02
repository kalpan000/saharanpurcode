# Django imports
from django.urls import path
from .views import InformationView,TerminalView
urlpatterns = [
    path('',InformationView.as_view(), name="dc"),
    path('terminal',TerminalView.as_view(), name="terminal"),
]