import json
import os
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.response import Response
from rest_framework import status
from .tasks import create_Prompt, save_message, check_product_related_task 
from django.views.decorators.clickjacking import xframe_options_exempt
from .Chatbot import start_bot , get_bot_responses, get_igcse_response
from .models import Key, Prompt_Template, ChatMessage
from .ProductsRelated import igcse_prompt_generate , check_educationRelated, youtubelinks , extract_words
from .image_analysis import get_image_analysis


PDFS_BASE_DIR = 'talkyai/pdfs'
RETRIEVER_BASE_DIR = 'talkyai/retriever'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def landing_page(request):
    return render(request, 'chatbot/landingpage.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def dashboard(request):
    list_key = Key.objects.filter(user = request.user)
   # list_key.delete()
    return render(request, 'chatbot/dashboard.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def create_bot(request):
    return render(request, 'chatbot/create_bot.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def edit_bot(request, key):
    if key:
            context = {'key': key}
    else:
            context = {'key': None}
    return render(request, 'chatbot/edit_bot.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def create_bot(request , key = None):
    if key:
        context = {'key': key}
        
    else :
        context = {'key': None}
    return render(request, 'chatbot/create_bot.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def hub(request):
    return render(request, 'chatbot/hub.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def hub(request , key = None):
    if key:
        context = {'key': key}
    else :
        context = {'key': None}
    return render(request, 'chatbot/hub.html' , context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def igcse(request):
    return render(request, 'chatbot/igcse.html')

@xframe_options_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chatbotiframe(request, key):
    print(key)
    return render(request, 'chatbot/chatbotiframe.html' , {'key': key})






# @api_view(['POST'])

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Create_Agent(request):
    try:
        data = request.data
        name = data.get('name')
        if name.lower() == 'igcse':
            return Response({'error': 'Model name is reserved'}, status=status.HTTP_400_BAD_REQUEST)
        botPurpose = data.get('purpose')
        botData = data.get('data')
        key_instance = Key(user=request.user, model_name = name)
        key_instance.save()
        id = key_instance.hash_key
        create_Prompt.delay( botPurpose, botData, key_instance.hash_key)

        response_data = {
            'message': 'Key has been stored successfully',
            'id': id
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        response_data = {'error': str(e)}
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_keys(request):
    try:
        # Fetch the keys related to the authenticated user
        #keys = Key.objects.filter(user=request.user)
        keys = Key.objects.filter(user=request.user).exclude(model_name='igcse')

        
        # Combine hash_key and model_name into a single list of dictionaries
        keylist = [
            {'hash_key': key.hash_key, 'model_name': key.model_name}
            for key in keys
        ]
        
        return Response(keylist, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_documents(request):
     try:
        uploaded_file = request.FILES.get('document')
        key_id = request.POST.get('key')
        
        print(key_id)
        if not uploaded_file:
            return Response({'error': 'File document is required'}, status=status.HTTP_400_BAD_REQUEST)

        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in ['.pdf', '.csv']:
            return Response({'error': 'Unsupported file type'}, status=status.HTTP_400_BAD_REQUEST)

        file_directory = os.path.join(PDFS_BASE_DIR, request.user.username, str(key_id))
        os.makedirs(file_directory, exist_ok=True)

        file_path = os.path.join(file_directory, uploaded_file.name)
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        file_list = [file for file in os.listdir(file_directory) if file.endswith(('.pdf', '.csv'))]

        return Response({'message': 'File uploaded successfully', 'files': file_list}, status=status.HTTP_200_OK)

     except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents(request, key):
    try:
        pdf_directory = os.path.join(PDFS_BASE_DIR, request.user.username, key)

        if not os.path.exists(pdf_directory):
            return Response({'error': 'No PDFs found for this bot ID'}, status=status.HTTP_404_NOT_FOUND)

        pdf_list = [pdf for pdf in os.listdir(pdf_directory) if pdf.endswith('.pdf') or pdf.endswith('.csv')]

        return Response({'pdfs': pdf_list}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request,  key , document):
    pdf_directory = os.path.join(PDFS_BASE_DIR, request.user.username, key)
    if not os.path.exists(pdf_directory):
        return Response({'error': 'No PDFs found for this bot ID'}, status=status.HTTP_404_NOT_FOUND)
    document_path = os.path.join(pdf_directory, document)
    if not os.path.exists(document_path):
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    os.remove(document_path)
    return Response({'message': 'Document deleted successfully'}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_prompt(request):

        data = request.data
        key_id = data.get('key')
        instructions = data.get('prompt')
        print(key_id)

        if not key_id:
            return Response({'error': 'Invalid input: key is required.'}, status=status.HTTP_400_BAD_REQUEST)

        key = get_object_or_404(Key, hash_key=key_id, user=request.user)

        # Retrieve the existing prompt instance
        prompt_instance = get_object_or_404(Prompt_Template, key=key)

        # Update the instructions field
        prompt_instance.instructions = instructions
        prompt_instance.save()
        return Response({'message': 'Instructions updated successfully'}, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chatbot(request , key):
    return render(request, 'chatbot/startbot.html/', {'key': key})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_Bot(request, key):
    key_id = key
    print(key_id)
    print(request.user.username)
    
    try:
        retriever_directory = os.path.join(RETRIEVER_BASE_DIR, request.user.username, key_id)
        pdf_directory = os.path.join(PDFS_BASE_DIR, request.user.username, key_id)
        print (pdf_directory)
        api_key = os.environ.get('OPENAI_API_KEY')
    

        if not api_key:
            return Response({'error': 'API key not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        answer_from_bot = start_bot(api_key, pdf_directory, retriever_directory)
        return Response({'message': 'Bot initialized using PDF.', 'response': answer_from_bot}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_bot_response(request):
    try:
        data = request.data
        question = data.get('question')
        key_id = data.get('key')

        if not question or not key_id:
            return Response({'error': 'Question and key are required'}, status=status.HTTP_400_BAD_REQUEST)

        prompt_template_obj = Prompt_Template.objects.filter(key_hash=key_id).first()
        if not prompt_template_obj:
            return Response({'error': 'Prompt template not found'}, status=status.HTTP_404_NOT_FOUND)

        prompt_template = prompt_template_obj.prompt
        instructions = prompt_template_obj.instructions
        retriever_directory = os.path.join(RETRIEVER_BASE_DIR, request.user.username, key_id)
        api_key = os.environ.get('OPENAI_API_KEY')

        if not api_key:
            return Response({'error': 'API key not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = get_bot_responses(api_key, question, prompt_template, retriever_directory, instructions)
        ip_address = request.META.get('REMOTE_ADDR')
        username = request.user.username
        check_product_related_task.delay(username, question, response, ip_address)

        save_message.delay(request.user.id, key_id, question, 'user')
        save_message.delay(request.user.id, key_id, response, 'bot')

        return Response({'response': response}, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def load_previous_messages(request, bot_id):
    chat_messages = ChatMessage.objects.filter(user=request.user, bot_id=bot_id).order_by('timestamp')
    messages = [{'message': msg.message, 'sender': msg.sender, 'timestamp': msg.timestamp} for msg in chat_messages]
    return Response({'messages': messages}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_chat(request, bot_id):
    ChatMessage.objects.filter(bot_id=bot_id).delete()
    return Response({'message': 'Chat messages deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def isEudcationalRelated(request):
    try:
        print("REQUEST HERE")
        data = request.data
        question = data.get('question')
        key_id = Key.objects.filter(model_name='igcse').first().hash_key
        if not question or not key_id:
            return Response({'error': 'Question and key are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        isEducationRelated = check_educationRelated(question)
        print(isEducationRelated)
        return Response({'response': isEducationRelated}, status=status.HTTP_200_OK)
    
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def igcse_response(request):
     try:
        data = request.data
        question = data.get('question')
        key_id = Key.objects.filter(model_name='igcse').first().hash_key
        if not question or not key_id:
            return Response({'error': 'Question and key are required'}, status=status.HTTP_400_BAD_REQUEST)
        prompt_template = igcse_prompt_generate(question)
    
        

        retriever_directory = os.path.join(RETRIEVER_BASE_DIR, request.user.username, key_id)
        api_key = os.environ.get('OPENAI_API_KEY')

        if not api_key:
            return Response({'error': 'API key not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response = get_igcse_response(api_key, prompt_template, retriever_directory)
     
        # save_message.delay(request.user.id, key_id, question, 'user')
        # save_message.delay(request.user.id, key_id, response, 'bot')

        return Response({'response': response}, status=status.HTTP_200_OK)

     except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

     except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_key(request, key_id):
    try:
        key_instance = get_object_or_404(Key, hash_key=key_id, user=request.user)

        # Delete the PDFs
        pdf_directory = os.path.join(PDFS_BASE_DIR, request.user.username, key_id)
        if os.path.exists(pdf_directory):
            for root, dirs, files in os.walk(pdf_directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(pdf_directory)

        # Delete the retriever directory
        retriever_directory = os.path.join(RETRIEVER_BASE_DIR, request.user.username, key_id)
        if os.path.exists(retriever_directory):
            for root, dirs, files in os.walk(retriever_directory, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(retriever_directory)

        # Delete the key instance
        key_instance.delete()

        return Response({'message': 'Key and associated files deleted successfully'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def image_analysis(request):
    data = request.data.get('image')
    print(data)
    analysis  = get_image_analysis(data)
    return Response({'response': analysis}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny]) 
def recommend_links(request):
    try:
        key = os.environ.get('YOUTUBE_API_KEY')
        bot_response = request.data.get('question')
        words = extract_words(bot_response)
        links = youtubelinks(key, words)
        print("Words:", words)
        return Response({'links': links}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
def sidebar(request):
    return render(request, 'chatbot/sidebar.html')

def navbar(request):
    return render(request, 'chatbot/navbar.html')
