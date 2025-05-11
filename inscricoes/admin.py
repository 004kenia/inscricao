from django.contrib import admin
from .models import (
    Aluno, PerfilAluno, Inscricao, EnvioMensagem,
    Curso, Evento, Testimonial, professor, Area
)



@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'message')
    
    from django.contrib import admin
from .models import Departamento, Docente, Disciplina, FormacaoAcademica, ExperienciaProfissional, AreaPesquisa, Publicacao

class DocenteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'departamento', 'get_nivel_display', 'get_cargo_display', 'ativo')
    list_filter = ('departamento', 'nivel', 'cargo', 'ativo')
    search_fields = ('nome', 'email')
    filter_horizontal = ('disciplinas', 'formacao', 'experiencia', 'areas_pesquisa', 'publicacoes')
    readonly_fields = ('data_cadastro', 'data_atualizacao')

admin.site.register(Departamento)
admin.site.register(Docente, DocenteAdmin)
admin.site.register(Disciplina)
admin.site.register(FormacaoAcademica)
admin.site.register(ExperienciaProfissional)
admin.site.register(AreaPesquisa)
admin.site.register(Publicacao)

admin.site.register(Aluno) 
admin.site.register(Area) 
admin.site.register(PerfilAluno)
admin.site.register(Inscricao)
admin.site.register(EnvioMensagem)
admin.site.register(Curso)
admin.site.register(Evento)
admin.site.register(professor)