import os
import openai
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts import ChatPromptTemplate
from .ProductsRelated import ProductClassifier
import hashlib
from django.core.files.base import ContentFile
from io import BytesIO
from .models import Analytics_Of_Bot, Chart

openai.api_key = os.getenv('OPENAI_API_KEY')

def save_chart_to_db(user, chart_type, fig):
    print(f"Saving chart {chart_type} to database...")
    try:
        buf = BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        chart = Chart(user=user, chart_type=chart_type)
        chart.image.save(f'{chart_type}.png', ContentFile(buf.read()), save=True)
        buf.close()
        print(f"Chart {chart_type} saved successfully.")
    except Exception as e:
        print(f"Error saving chart {chart_type}: {e}")
    return chart

def generate_charts(user):
    try:
        print("Fetching analytics data...")
        all_analytics =   Analytics_Of_Bot.objects.all().filter(username=user)
        analytics_list = list(all_analytics.values('username', 'question', 'response', 'ip_address'))
        df = pd.DataFrame(analytics_list)

        if df.empty or 'response' not in df.columns:
            print("No data available to generate charts.")
            return

        df = df[df['response'].str.strip() != '']
        analytics_list = [item for item in analytics_list if item.get('response') and item['response'].strip()]

        print("Generating chart: Number of Questions Asked by Each User")
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='username', order=df['username'].value_counts().index)
        plt.title('Number of Questions Asked by Each User')
        plt.xlabel('Username')
        plt.ylabel('Number of Questions')
        plt.xticks(rotation=45)
        fig = plt.gcf()
        save_chart_to_db(user, 'Questions asked by User', fig)

        print("Generating chart: Proportion of Unique vs Duplicate Questions")
        unique_questions = df['question'].nunique()
        plt.figure(figsize=(6, 6))
        plt.pie([unique_questions, len(df) - unique_questions], labels=['Unique Questions', 'Duplicate Questions'], autopct='%1.1f%%', startangle=140)
        plt.title('Proportion of Unique vs Duplicate Questions')
        fig = plt.gcf()
        save_chart_to_db(user, 'Unique Vs Duplicate Questions', fig)

        print("Generating chart: Number of Questions Asked from Each IP Address")
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='ip_address', order=df['ip_address'].value_counts().index)
        plt.title('Number of Questions Asked from Each IP Address')
        plt.xlabel('IP Address')
        plt.ylabel('Number of Questions')
        plt.xticks(rotation=45)
        fig = plt.gcf()
        save_chart_to_db(user, 'Ip addresses of User', fig)

        print("Generating chart: Distribution of Response Lengths")
        df['response_length'] = df['response'].apply(len)
        plt.figure(figsize=(10, 6))
        sns.histplot(df['response_length'], bins=20, kde=True)
        plt.title('Distribution of Response Lengths')
        plt.xlabel('Response Length')
        plt.ylabel('Frequency')
        fig = plt.gcf()
        save_chart_to_db(user, 'AI Response Length', fig)

        responses = [item['response'] for item in analytics_list if item.get('response') and item['response'].strip()]

        print("Classifying products from responses...")
        api_key = os.getenv('OPENAI_API_KEY')
        product_classifier = ProductClassifier(api_key=api_key)

        prompt_template = (
        "Extract the list of products along with their frequency(Suppose: Product - 1) mentioned in the following responses:\n\n"
        "{response_list}"
        "Do not Use Bold letters."
        )
        inputs = {"response_list": responses}
        products_text = product_classifier.classify_text(inputs, prompt_template)

        # Parsing the product classifier response
        product_list = []
        for line in products_text.strip().split('\n'):
            try:
                product_name, count = line.split(' - ')
                count = int(count)
                product_list.append((product_name.strip(), count))
            except ValueError:
                continue

        df_products = pd.DataFrame(product_list, columns=["Product", "Count"])


        print("Generating chart: Proportion of Each Product Category (Top 5)")
        top_5_products = df_products.nlargest(5, 'Count')
        plt.figure(figsize=(10, 8))
        plt.pie(top_5_products['Count'], labels=top_5_products['Product'], autopct='%1.1f%%', startangle=140)
        plt.title('Proportion of Each Product Category (Top 5)')
        fig = plt.gcf()
        save_chart_to_db(user, 'Product Proportions (Top 5)', fig)

        # Generating Box Plot of Product Frequencies
        print("Generating chart: Box Plot of Product Frequencies")
        plt.figure(figsize=(14, 10))
        sns.boxplot(x='Product', y='Count', data=df_products)
        plt.title('Box Plot of Product Frequencies')
        plt.xlabel('Product')
        plt.ylabel('Frequency')
        plt.xticks(rotation=90)
        fig = plt.gcf()
        save_chart_to_db(user, 'Box Plot Frequencies', fig)

        # Generating Line Plot of Product Counts Over Indices
        print("Generating chart: Line Plot of Product Counts Over Indices")
        plt.figure(figsize=(14, 10))
        sns.lineplot(x=df_products.index, y='Count', data=df_products)
        plt.title('Line Plot of Product Counts Over Indices')
        plt.xlabel('Index')
        plt.ylabel('Product Count')
        fig = plt.gcf()
        save_chart_to_db(user, 'Line Plot Counts', fig)

        print("Generating chart: Bubble Chart of Product Frequencies")
        plt.figure(figsize=(14, 10))
        plt.scatter(x=df_products['Product'], y=df_products['Count'], s=df_products['Count'] * 100, alpha=0.5, color='purple')
        plt.title('Bubble Chart of Product Frequencies')
        plt.xlabel('Product')
        plt.ylabel('Frequency')
        plt.xticks(rotation=90)
        fig = plt.gcf()
        save_chart_to_db(user, 'Bubble Chart', fig)

        print("Finished generating all charts.")
    except Exception as e:
        print(f"Error during chart generation: {e}")

    return True
