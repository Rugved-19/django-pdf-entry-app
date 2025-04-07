from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('register/', views.register_user, name='register_user'),
    path('<int:user_id>/', views.user_page, name='user_page'),
    path('add_entry/<int:user_id>/', views.add_entry, name='add_entry'),
   # pdf_app/urls.py
  path('delete_entry/<int:user_id>/<int:entry_id>/', views.delete_entry, name='delete_entry'),
path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),


path('delete_all_entries_global/', views.delete_all_entries_global, name='delete_all_entries_global'),


    path('delete_all_entries/<int:user_id>/', views.delete_all_entries, name='delete_all_entries'),
    path('generate_pdf_user/<int:user_id>/', views.generate_pdf_user, name='generate_pdf_user'),  # ✅ Add this
    path('generate_pdf_all/', views.generate_pdf_all, name='generate_pdf_all'),
    path('generate_combined_pdf/', views.generate_combined_pdf, name='generate_combined_pdf'),
]
