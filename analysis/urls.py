from django.urls import path
from . import views

urlpatterns = [ 
  path('', views.home, name='home'),  # رابط صفحة الرئيسية
  path('dashboard/', views.dashboard, name='dashboard'),  # رابط لعرض النتائج
  path('upload/', views.upload, name='upload'),  # رابط لرفع الملفات
  path('history/', views.history, name='history'),  # رابط صفحة الهيستوري
  path('download/<int:history_id>/', views.download_pdf, name='download_pdf'),
  path('contact/', views.contact_us, name='contact'),  # رابط تواصل معنا
  path('profile/', views.profile, name='profile'),  # رابط صفحة الملف الشخصي
  path('about/', views.about, name='about'),  # رابط صفحة عن بيان
  path('login/', views.login_user, name='login'),
  path('register/', views.register_user, name='register'),
  path('logout/', views.logout_user, name='logout'),
  path('save-profile/', views.update_profile, name='save_profile'),
  path('save-merchant/', views.save_merchant, name='save_merchant'),
]