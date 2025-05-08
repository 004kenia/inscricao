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

admin.site.register(Aluno) 
admin.site.register(Area) 
admin.site.register(PerfilAluno)
admin.site.register(Inscricao)
admin.site.register(EnvioMensagem)
admin.site.register(Curso)
admin.site.register(Evento)
admin.site.register(professor)