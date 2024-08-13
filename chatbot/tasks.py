import os
import multiprocessing
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from celery import shared_task
from .ProductsRelated import create_chatbot, check_product_related
from chatbot.models import  Prompt_Template , Analytics_Of_Bot , ChatMessage
import logging
from django.core.mail import send_mail
import smtplib



# Set the start method to 'spawn'
multiprocessing.set_start_method('spawn', force=True)

@shared_task
def check_product_related_task(username, question, response, ip_address):
    # Check if the response is product-related
    is_product = check_product_related(response , question)
    print(f'Product related checking: {is_product}')

    # If it is product-related, save to the database
    if is_product:
        # Create a new instance of the Analytics model
        analytics_entry = Analytics_Of_Bot(
            username = username,
            response=response,
            question=question,
            ip_address = ip_address
        )
        # Save the entry to the database
        analytics_entry.save()
        print(analytics_entry)
        print('Saved to the database')





    
    

# def format_email_content(analytics_data):
#     if 'error' in analytics_data:
#         return f"<h1>Error fetching analytics data: {analytics_data['error']}</h1>"

#     content = f"""
#     <h1>Analytics Data</h1>
#     <p><strong>User Count:</strong> {analytics_data['user_count']}</p>
#     <p><strong>Usernames:</strong> {', '.join(analytics_data['usernames'])}</p>
#     <h2>Responses:</h2>
#     <ul>
#     """
    
#     for response in analytics_data['responses']:
#         content += f"<li>{response}</li>"
    
#     content += "</ul><h2>Detailed Analytics:</h2><table border='1'><tr><th>Username</th><th>Question</th><th>Response</th><th>IP Address</th></tr>"

#     for entry in analytics_data['analytics']:
#         content += f"<tr><td>{entry['username']}</td><td>{entry['question']}</td><td>{entry['response']}</td><td>{entry['ip_address']}</td></tr>"
    
#     content += "</table>"

#     return content



# @shared_task
# def send_email():
#     # Fetch analytics data
#     analytics_data = GetFullAnalytics()
#     # Format email 
#     email_content = format_email_content(analytics_data)
#     content = email_content
#     SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
#     api_key = SENDGRID_API_KEY
#     from_email = 'info@learnity.store'
#     to_emails = 'umar1671594@gmail.com'
#     subject = 'Analytics Data'

    
#     message = Mail(
#         from_email=from_email,
#         to_emails=to_emails,
#         subject=subject,
#         html_content=content
#     )
#     try:
#         sg = SendGridAPIClient(api_key)
#         response = sg.send(message)
#         return response.status_code, response.body, response.headers
#     except Exception as e:
#         return str(e)



from django.shortcuts import get_object_or_404
from .models import Key



@shared_task
def create_Prompt(purpose, data, key_id):
    print("test")
    key = get_object_or_404(Key, hash_key=key_id)
    
    chatbot = create_chatbot(purpose, data)
    print(chatbot)
    if chatbot:
        prompt = Prompt_Template(prompt=chatbot, key=key)
        prompt.save()
        print('Prompt saved successfully')
    else:
        print('Failed to create chatbot prompt')
    print("working")




@shared_task
def save_message(user_id, bot_id, message, sender):
    # Save the chat message to the database
    chat_message = ChatMessage(
        user_id=user_id,
        bot_id=bot_id,
        message=message,
        sender=sender
    )
    chat_message.save()
    print('Chat message saved successfully')
    return chat_message.id


