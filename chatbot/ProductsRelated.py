import os
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import ChatPromptTemplate
from django.http import JsonResponse
from .models import Analytics_Of_Bot
import requests
from dotenv import load_dotenv
load_dotenv()


class ProductClassifier:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.llm = None
        self.api_key = api_key

    def _create_chain(self, prompt_template: str) -> LLMChain:
        # Initialize the OpenAI Chat LLM
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=self.api_key , temperature=0.5)
        
        # Create a ChatPromptTemplate
        template = ChatPromptTemplate.from_template(template=prompt_template)
        
        # Create and return an LLMChain
        return LLMChain(llm=self.llm, prompt=template)

    def classify_text(self, inputs: dict, prompt_template: str) -> str:
        chain = self._create_chain(prompt_template)
        response = chain.run(inputs)
        return response.strip()
    
    def extract_keywords(self, text:str) -> str:
        prompt_template = '''
        From the given text below, extract the 3 best keywords that could be used to search youtube for relevant videos. For example 'Trigonometry'.
        Text: "{text}"'''
        inputs = {"text": text}
        response = self.classify_text(inputs, prompt_template)
        return response
     
    def igcse_prompt_generate(self, text:str) -> str:
        prompt_template = """
        Role play as a prompt engineer and create a prompt. The prompt's purpose is to guide students.
        The student's requirements are {text}. Create dynamic prompt for the llm so that the llm can role play as per the requirements of the user. For example: You are are Physics teacher.
        Keep the prompt short and simple.
        """
        inputs = {"text": text}
        response = self.classify_text(inputs, prompt_template)
        return response
    def check_is_education_related(self, text: str) -> bool:
        prompt_template = """
        Determine if the question and its answer below is education related or not.
        Text: "{text}"
        Answer with 'Yes' or 'No' ONLY.
        """
        inputs = {"text": text}
        answer = self.classify_text(inputs, prompt_template).lower()
        if answer in ['yes', 'no']:
            return answer == 'yes'
        else:
            raise ValueError("Unexpected response from the model")
    def is_product_related(self, text: str) -> bool:
        prompt_template = """
        Determine if the question and its answer below is product related or not.
        Text: "{text}"
        Answer with 'Yes' or 'No' ONLY.
        """
        inputs = {"text": text}
        answer = self.classify_text(inputs, prompt_template).lower()
        if answer in ['yes', 'no']:
            return answer == 'yes'
        else:
            raise ValueError("Unexpected response from the model")

    def generate_prompt(self, botpurpose: str, botdata: str) -> str:
        prompt_template = """
        Role play as a prompt engineer and create a prompt. The prompt's purpose is {botpurpose} and the data is {botpurpose}.
        You will use these 2 details to design a perfect prompt which will instruct the llm todo tasks. Use you as pronoun for example You are a retail expert.
        Keep the prompt short and simple.
        
        """
        inputs = {"botpurpose": botpurpose, "botdata": botdata}
        response = self.classify_text(inputs, prompt_template)
        return response

def check_product_related(answer: str, question: str) -> bool:
    text_to_check = f"Question: {question} Answer: {answer}"
    print(text_to_check)
    
    api_key = os.getenv('OPENAI_API_KEY')
    classifier = ProductClassifier(api_key)
    
    is_related = classifier.is_product_related(text_to_check)
    return is_related

    
def create_chatbot(botpurpose: str, botdata: str) -> LLMChain:
    api_key = os.environ.get('OPENAI_API_KEY')
    print(api_key)
    classifier = ProductClassifier(api_key)
    generated_prompt = classifier.generate_prompt(botpurpose, botdata)
    return generated_prompt


def igcse_prompt_generate(query):
    api_key = os.getenv('OPENAI_API_KEY')
    
    classifier = ProductClassifier(api_key)
    
    # Define the text you want to generate a prompt for
    test_text = query
    
    # Call the igcse_prompt_generate method
    generated_prompt = classifier.igcse_prompt_generate(test_text)
    
    print(generated_prompt)
    return generated_prompt

def check_educationRelated(text):
    api_key = os.getenv('OPENAI_API_KEY')
    classifier = ProductClassifier(api_key)
    is_related = classifier.check_is_education_related(text)
    return is_related


def youtubelinks( api_key , search_query):

        
    search_query = search_query

        # URL for the YouTube Data API search endpoint
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&type=video&key={api_key}'


    # Make the request to the YouTube Data API
    response = requests.get(url)
 
    # Parse the response as JSON
    data = response.json()
 

    # Extract video links
    video_links = []
    for item in data['items']:
        print(item)
        video_id = item['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        video_links.append(video_url)
        
        
    print(video_links)
    return video_links




def extract_words(text):
    api_key = os.getenv('OPENAI_API_KEY')
    classifier = ProductClassifier(api_key)
    keywords = classifier.extract_keywords(text)
    return keywords


# def GetFullAnalytics():
#     try:
#         all_analytics = Analytics_Of_Bot.objects.all()
#         user_count = Analytics_Of_Bot.objects.values('username').distinct().count()
#         usernames = list(Analytics_Of_Bot.objects.values_list('username', flat=True).distinct())
#         responses = list(Analytics_Of_Bot.objects.values_list('response', flat=True))
#         analytics_list = list(all_analytics.values('username', 'question', 'response', 'ip_address'))

#         response_data = {
#             'user_count': user_count,
#             'usernames': usernames,
#             'responses': responses,
#             'analytics': analytics_list
#         }
#         print (GetFullAnalytics)
#         return response_data
#     except Exception as e:
#         return {'error': str(e)}
    
def GetAnalyticsList(name):
    try:
        all_analytics = Analytics_Of_Bot.objects.all().filter(username=name)
        analytics_list = list(all_analytics.values('username', 'question', 'response', 'ip_address'))
   
        return analytics_list
    except Exception as e:
        return {'error': str(e)}



