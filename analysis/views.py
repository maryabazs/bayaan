from django.shortcuts import render, redirect
import pandas as pd
from django.conf import settings
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import os 
import json
from io import BytesIO
import kaleido
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import pandas as pd
from transformers import pipeline
from django.http import JsonResponse
from time import sleep
import plotly.io as pio
import plotly.graph_objects as go
from django.shortcuts import render, redirect
import base64
import io
from django.core.files.base import ContentFile
from PIL import Image
import base64
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from .forms import SignUpForm, ProfilePictureForm
from django import forms
from django.contrib import messages
import datetime
import math
from .models import History, Analysis, Person, Merchant

import arabic_reshaper
from bidi.algorithm import get_display
import imgkit
import dataframe_image as dfi


def clean_and_reshape_text(text):  # فنكشن تخلي الكلام مضبوط في الورد كلاود
    reshaped_text = arabic_reshaper.reshape(text)  # إعادة ترتيب النص
    bidi_text = get_display(reshaped_text)         # fixes RTL direction
    return bidi_text

# توليد الورد كلاود بناءً على النصوص
def generate_wordcloud(text, id):
    # font_path = r"font/NotoNaskhArabic-Regular.ttf"
    # font_path = r"font/Amiri-Regular.ttf"
    font_path = r"C:\Users\mo905\OneDrive\Desktop\bayan103\font\NotoNaskhArabic-Regular.ttf"
    # font_path = os.path.abspath("/Users/amr/work/bayan/font/Cairo-Regular.ttf")
    
    # تنظيف النص قبل توليد سحابة الكلمات
    reshaped_text = clean_and_reshape_text(text)
    
    wordcloud = WordCloud(
        width=500, 
        height=400, 
        background_color='rgba(255, 255, 255, 0)', 
        font_path=font_path ,  # تحديد الخط هنا
        colormap='Blues'
    ).generate(reshaped_text)
    
    # حفظ الصورة كـ PNG أو تحويلها إلى base64 لإظهارها في واجهة المستخدم
    
    wordcloud.to_file(f"word_{id}.png")
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return img_base64

# قائمة الموديلات المتاحة لتحليل المشاعر
AVAILABLE_MODELS = [
    "CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment",  # مودل CAMeL-BERT
    "aubmindlab/bert-large-arabertv02-twitter"           # مودل AraBERT (نسخة تويتر)
]

# فنكشن معالجة رفع الملفات من قبل المستخدم
def upload(request):
    if not request.user.is_anonymous:
        person = Person.objects.get(user=request.user)
        if request.method == 'POST' and request.FILES['reviews_file']:
        # الحصول على المودل المختارمن طلب اليوزر
            selected_model = request.POST.get('model', AVAILABLE_MODELS[0])  # اختيار المودل الافتراضي إذا لم يتم تحديد مودل

            # تحميل المودل المحدد لتحليل المشاعر
            sentiment_analyzer = pipeline("sentiment-analysis", model=selected_model)

            # قراءة الملف المرفوع من قبل المستخدم
            file = request.FILES['reviews_file']
            
            
            try:
                df = pd.read_excel(file)
                df.rename(columns={'المحتوى': 'review', 'المنتج': 'product'}, inplace=True)

                if 'review' not in df.columns or 'product' not in df.columns:
                    return render(request, 'upload.html', {'error': 'الملف يجب أن يحتوي على عمود "review" و "product"'})

                df = df.dropna(subset=['review'])
                all_reviews_text = ' '.join(df['review'].dropna())

                sentiments = []
                for review in df['review']:
                    result = sentiment_analyzer(review)
                    sentiments.append(result[0]['label'])

                df['sentiment'] = sentiments
                df['sentiment'] = df['sentiment'].replace({'LABEL_0': 'سلبي', 'LABEL_1': 'ايجابي', 'LABEL_2': 'محايد'})
                # this code for added history to db
                file_name = file.name
                file_type = file_name.split('.')[-1]
                file_size = f"{math.ceil(file.size / 1024)} kb"
                history = History.objects.create(
                    file_name=file_name,
                    type=file_type,
                    size=file_size,
                    user=request.user,
                    event=True
                )
                history.save()
                history_id = history.id
                # this code for dashboard
                product_sentiments = df.groupby('product')['sentiment'].value_counts().unstack().fillna(0)
                fig2 = go.Figure()
                for product in product_sentiments.index:
                    fig2.add_trace(go.Bar(
                        x=product_sentiments.columns,
                        y=product_sentiments.loc[product],
                        name=product
                    ))
                fig2.update_layout(
                    barmode='stack',
                    xaxis_title="تصنيف المشاعر",
                    yaxis_title="العدد",
                    legend_title="المنتج",
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    font=dict(color="black")
                )
                graph_html2 = fig2.to_html(full_html=False)
                sentiment_counts = df['sentiment'].value_counts()
                fig = go.Figure(data=[ 
                    go.Pie(
                        labels=sentiment_counts.index,
                        values=sentiment_counts,
                        hoverinfo='label+percent',
                        textinfo='value+percent',
                        marker=dict(colors=['#cce5ff', '#99c2ff', '#66b3ff'])   
                    )
                ])
                fig.update_layout(
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    font=dict(color="black")
                )
                graph_html = fig.to_html(full_html=False)
                positive_count = sentiment_counts.get('positive', 0)
                negative_count = sentiment_counts.get('negative', 0)
                neutral_count = sentiment_counts.get('neutral', 0)
                total_reviews = positive_count + negative_count + neutral_count
                positive_ratio = (positive_count / total_reviews) * 100 if total_reviews > 0 else 0
                fig3 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=positive_ratio,
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "lightgrey"},
                        'steps': [
                            {'range': [0, 40], 'color': "cyan"},
                            {'range': [40, 70], 'color': "royalblue"},
                            {'range': [70, 100], 'color': "darkblue"}
                        ],
                    }
                ))
                graph_html3 = fig3.to_html(full_html=False)
                # this code for history 
                df['product'] = df['product'].apply(lambda x: get_display(arabic_reshaper.reshape(x)))
                product_sentiments = df.groupby(['product', 'sentiment']).size().unstack(fill_value=0)
                product_sentiments.plot(kind='bar', stacked=True, colormap='viridis', figsize=(8, 6),)
                plt.title(get_display(arabic_reshaper.reshape('تحليل المشاعر')))
                plt.xlabel(get_display(arabic_reshaper.reshape('تصنيف المشاعر')))
                plt.ylabel(get_display(arabic_reshaper.reshape('العدد')))
                plt.legend(title=get_display(arabic_reshaper.reshape('المنتج'))) 
                plt.tight_layout()
                plt.savefig(f"product_{history_id}.png")   
                plt.close()
                sentiment_counts = df['sentiment'].value_counts()
                labels = sentiment_counts.index 
                sizes = sentiment_counts.values
                plt.figure(figsize=(6, 6))
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#cce5ff', '#99c2ff', '#66b3ff'])
                plt.title(clean_and_reshape_text('نسب المشاعر'))
                plt.savefig(f"sentiment_{history_id}.png")
                plt.close()
                positive_count = sentiment_counts.get('positive', 0)
                negative_count = sentiment_counts.get('negative', 0)
                neutral_count = sentiment_counts.get('neutral', 0)
                total_reviews = positive_count + negative_count + neutral_count
                positive_ratio = (positive_count / total_reviews) * 100 if total_reviews > 0 else 0
                plt.figure(figsize=(6, 6))
                plt.barh([0], [positive_ratio], color="royalblue")
                plt.xlim(0, 100)
                plt.title(clean_and_reshape_text('نسبه المراجعات الايجابيه'))
                plt.yticks([])
                plt.xlabel('%')
                plt.savefig(f'positive_{history_id}.png')
                plt.close()
                # Convert DataFrame to List of Lists
                df_styled = df.style.background_gradient()
                wordcloud_img_base64 = generate_wordcloud(all_reviews_text, history_id)
                df.rename(columns={'review': 'المحتوى', 'product': 'المنتج'}, inplace=True)
                dfi.export(df_styled, f'data_{history_id}.png')
                main_director = f"{os.path.dirname(os.path.abspath(__file__))}"
                main_director = main_director.split('analysis')[0]
                customer_review = f"{main_director}/data_{history_id}.png"
                word_cloud = f"{main_director}/word_{history_id}.png"
                positive_file = f"{main_director}/positive_{history_id}.png"
                product_file = f"{main_director}/product_{history_id}.png"
                sentiment_file = f"{main_director}/sentiment_{history_id}.png"
                img = Image.open(customer_review)
                img2 = Image.open(word_cloud)
                img3 = Image.open(positive_file)
                img4 = Image.open(product_file)
                img5 = Image.open(sentiment_file)
                img_io = io.BytesIO()
                img2_io = io.BytesIO()
                img3_io = io.BytesIO()
                img4_io = io.BytesIO()
                img5_io = io.BytesIO()
                img.save(img_io, format='PNG')
                img2.save(img2_io, format='PNG')
                img3.save(img3_io, format='PNG')
                img4.save(img4_io, format='PNG')
                img5.save(img5_io, format='PNG')
                customer_image = ContentFile(img_io.getvalue(), name=f'data_{history_id}.png')
                word_image = ContentFile(img2_io.getvalue(), name=f'word_{history_id}.png')
                overall_image = ContentFile(img5_io.getvalue(), name=f'sentiment_{history_id}.png')
                product_image = ContentFile(img4_io.getvalue(), name=f'product_{history_id}.png')
                positive_image = ContentFile(img3_io.getvalue(), name=f'positive_{history_id}.png')
            
                analysis = Analysis.objects.create(
                    customer_review=customer_image,
                    overall_sentiment=overall_image,
                    product_sentiment=product_image,
                    word_cloud=word_image,
                    positive_sentiment=positive_image,
                    history=history,
                )
                analysis.save()
                messages.success(request, "Uploading Success")
                df.rename(columns={'المحتوى': 'review', 'المنتج': 'product'}, inplace=True)
                return render(request, 'analysis/dashboard.html', {
                    'df': df, 
                    'graph_html': graph_html, 
                    'graph_html2': graph_html2,
                    'graph_html3': graph_html3,
                    'wordcloud_img': wordcloud_img_base64,
                    'positive_count': positive_count,
                    'negative_count': negative_count,
                    'neutral_count': neutral_count,
                    'show_modal': True,
                    'person': person,
                })
            
            except Exception as e:
                return render(request, 'analysis/upload.html', {'error': f'حدث خطأ أثناء قراءة الملف: {str(e)}', 'person': person})
        else:
            return render(request, 'analysis/upload.html', {'person': person})
    else: 
        return render(request, 'analysis/upload.html')


def dashboard(request):
    return render(request, 'analysis/dashboard.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('upload')
        else:
            messages.error(request, "You don't have an account, go to create a new")
            return render(request, 'analysis/login.html', {'show_modal': True})
    else:
        return render(request, 'analysis/login.html')

def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            # log in user
            user = authenticate(request, username=username, password=password, email=email)
            person = Person.objects.create(
                user = user,
                phone="",
            )
            person.save()
            login(request, user)
            messages.success(request, "You are now registered.")
            return redirect('upload')
        else:
            messages.error(request, "There was a problem. Please try again.")
            return render(request, 'analysis/register.html', {'form': form, 'show_modal': True})
    else:
        return render(request, 'analysis/register.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

def home(request):
    return render(request, 'analysis/home.html')

def download_pdf(request, history_id):
    analysis = Analysis.objects.get(history__id=history_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="analysis_report.pdf"'

    # Create a PDF canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin

    def check_page_break(y, space_needed=580):
        """Helper to start a new page if there's not enough space."""
        if y - space_needed < margin:
            p.showPage()
            return height - margin
        return y

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, y, "📝 Analysis Report")
    y -= 40

    # Helper to draw image if exists
    def draw_image(image_field, label, y):
        if image_field:
            img_path = os.path.join(settings.MEDIA_ROOT, str(image_field))
            if os.path.exists(img_path):
                y = check_page_break(y, 580)
                p.setFont("Helvetica", 12)
                p.drawString(margin, y, f"{label}:")
                y -= 20
                try:
                    p.drawImage(img_path, margin, y - 550, width=400, height=550, preserveAspectRatio=True)
                    y -= 570
                except Exception as e:
                    p.drawString(margin, y, f"(Could not load image: {e})")
                    y -= 20
        return y

    # Draw available images
    y = draw_image(analysis.customer_review, "Customer Review Image", y)
    y = draw_image(analysis.overall_sentiment, "Overall Sentiment", y)
    y = draw_image(analysis.product_sentiment, "Product Sentiment", y)
    y = draw_image(analysis.positive_sentiment, "Positive Sentiment", y)
    y = draw_image(analysis.word_cloud, "Word Cloud", y)

    # Finish and return PDF
    p.showPage()
    p.save()

    return response

def history(request):
    if request.user.is_anonymous:
        return render(request, 'analysis/history.html') 
    else:
        user = request.user
        person = Person.objects.get(user=user)
        histories = History.objects.filter(user=user)
        return render(request, 'analysis/history.html', {'histories': histories, 'person': person})


def contact_us(request):
    return render(request, 'analysis/contact.html')

def profile(request):
    user = request.user
    person = Person.objects.get(user=user)
    merchant, created = Merchant.objects.get_or_create(user=user)
    if request.method == 'POST' and request.FILES:
        person.image = request.FILES['file']
        person.save()
        return JsonResponse({'success': True, 'image': person.image.url})
    return render(request, 'analysis/profile.html', {'person': person, 'merchant': merchant})

@csrf_exempt
def update_profile(request):
    person = Person.objects.get(user=request.user)
    if request.method == 'POST':
        data = json.loads(request.body)
        person.phone = data.get('phone', '')
        person.location = data.get('location', '')
        person.save()
        return JsonResponse({'status': 'Success'})
    return JsonResponse({'status': 'Error'}, status=400)

@csrf_exempt
def save_merchant(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        merchant, _ = Merchant.objects.get_or_create(user=request.user)
        
        merchant.store_name = data.get('store_name', '')
        merchant.store_link = data.get('store_link', '')
        merchant.category = data.get('category', '')
        merchant.save()
        return JsonResponse({'status': 'Success'})
    return JsonResponse({'status': 'Error'}, status=400)

def about(request):
    return render(request, 'analysis/about.html')


