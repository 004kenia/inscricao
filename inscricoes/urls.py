from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', views.admin, name = 'admin'),
    path('bem_vindo/', views.bem_vindo, name = 'bem_vindo'),
    path('valida_login_aluno/', views.valida_login_aluno, name = 'valida_login_aluno'),
    path('valida_cadastro_aluno', views.valida_cadastro_aluno, name = 'valida_cadastro_aluno'),
    path('ficha/', views.ficha, name = 'ficha'),
    path('inscricao/', views.salvar_inscricao, name='inscricao'),
    path('cursos/', views.cursos, name='cursos'),
    path('eventos/', views.eventos, name='eventos'),
    path('evento/<int:id>/', views.detalhe_evento, name='detalhe_evento'),
    path('curso/<int:id>/', views.detalhe_curso, name='detalhe_curso'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
