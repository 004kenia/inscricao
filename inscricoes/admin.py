from django.contrib import admin
from .models import (
    Aluno, PerfilAluno, Inscricao, EnvioMensagem,
    Curso, Evento
)
from django.utils.html import format_html


class BaseSomenteLeitura(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


class AlunoAdmin(BaseSomenteLeitura):
    readonly_fields = [field.name for field in Aluno._meta.fields]


class InscricaoAdmin(BaseSomenteLeitura):
    readonly_fields = [field.name for field in Inscricao._meta.fields]


class EnvioMensagemAdmin(admin.ModelAdmin):  
    list_display = ['mensagem', 'data_envio', 'enviado', 'progresso']

    def mensagem_preview(self, obj):
        if obj.mensagem:
            return format_html('<p>{}</p>', obj.mensagem)
        return "Sem mensagem"
    mensagem_preview.short_description = "Visualização da Mensagem"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.enviado and obj.mensagem:
            enviar_email_em_massa.delay(obj.id)


class CursoAdmin(BaseSomenteLeitura):
    readonly_fields = ['imagem_preview', 'pdf_preview'] + [f.name for f in Curso._meta.fields]

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" width="200" />', obj.imagem.url)
        return "Sem imagem"
    imagem_preview.short_description = "Visualização da Imagem"
    
    def pdf_preview(self, obj):
        if obj.pdf_arquivo:
            return format_html('<a href="{}" target="_blank">Visualizar PDF</a>', obj.pdf_arquivo.url)
        return "Sem PDF"
    pdf_preview.short_description = "Visualizar PDF"


class EventoAdmin(BaseSomenteLeitura):
    readonly_fields = ['imagem_preview', 'pdf_preview'] + [f.name for f in Evento._meta.fields]

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" width="200" />', obj.imagem.url)
        return "Sem imagem"
    imagem_preview.short_description = "Visualização da Imagem"
    
    def pdf_preview(self, obj):
        if obj.pdf_arquivo:
            return format_html('<a href="{}" target="_blank">Visualizar PDF</a>', obj.pdf_arquivo.url)
        return "Sem PDF"
    pdf_preview.short_description = "Visualizar PDF"


class PerfilAlunoAdmin(BaseSomenteLeitura):
    readonly_fields = ['imagem_preview'] + [f.name for f in PerfilAluno._meta.fields]

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" width="100" />', obj.imagem.url)
        return "Sem imagem"
    imagem_preview.short_description = "Imagem de Perfil"


admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Inscricao, InscricaoAdmin)
admin.site.register(Curso, CursoAdmin)
admin.site.register(Evento, EventoAdmin)
admin.site.register(PerfilAluno, PerfilAlunoAdmin)
admin.site.register(EnvioMensagem, EnvioMensagemAdmin)  
