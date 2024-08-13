from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'chatbot'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_bot/<str:key>/', views.create_bot, name='create_bot'),  # This pattern should come first
    path('create_bot/', views.create_bot, name='create_bot'),
    path('create_agent/', views.Create_Agent, name='create_agent'),
    path('list-keys/', views.list_keys, name='list_keys'),
    path('edit_bot/<str:key>/', views.edit_bot, name='edit_bot'),
    path('add-document/', views.add_documents, name='add_document'),
    path('list-documents/<str:key>/', views.list_documents, name='list_documents'),
    path('delete-document/<str:key>/<str:document>/', views.delete_document, name='delete_document'),
    path('hub/<str:key>/', views.hub, name='hub'),
    path('hub/', views.hub, name='hub'),
    path('save-prompt/', views.save_prompt, name='save_prompt'),
    path('start-bot/<str:key>', views.chatbot, name='start_bot'),
    path('startbot/<str:key>', views.chatbotiframe, name='start_bot'),
    path('bot/<str:key>/', views.initiate_Bot, name='bot'),
    path('get-bot-response/', views.get_bot_response, name='get_bot_response'),
    path('load-previous-messages/<str:bot_id>/', views.load_previous_messages, name='load_previous_messages'),
    path('delete-chat/<str:bot_id>/', views.delete_chat, name='delete_chat'),   
    path('igcse/', views.igcse, name='igcse'),
    path ('igcse-response/', views.igcse_response, name='igcse_response'),
    path('delete-key/<str:key_id>/', views.delete_key, name='delete_key'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)