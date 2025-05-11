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
    path('termo/', views.termo, name = 'termo'),
    path('login/', views.login, name = 'login'),
    path('test-404/', views.trigger_404),
    path('cadastro/', views.cadastro, name = 'cadastro'),
    path('inscricao-detalhes/<int:inscricao_id>/', views.inscricao_detalhes, name='inscricao_detalhes'),
    path('professor/', views.professor, name = 'professor'),
    path('todos_cursos/', views.todos_cursos, name='todos_cursos'),
    path('lab/', views.lab, name = 'lab'),
    path('empresa/', views.empresa, name = 'empresa'),
    path('docentes/', views.corpo_docente, name='corpo_docente'),
    path('docentes/<int:docente_id>/modal/', views.docente_modal, name='docente_modal'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
