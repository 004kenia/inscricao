from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import path  # Certifique-se de importar a função 'path'
from .models import Aluno, EnvioMensagem, Inscricao
from .models import Curso
from .models import Evento

# Personalizando o admin
admin.site.site_header = "Bem Vindo admin"
admin.site.site_title = "Admin da Aplicação"
admin.site.index_title = "Bem-vindo à Administração"

# Registrando o modelo Aluno (apenas uma vez)
admin.site.register(Aluno)

# Removendo a linha abaixo, pois já usamos o decorador @admin.register
# admin.site.register(EnvioMensagem)

# Personalizando a administração do User
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'date_joined')

# Desregistrando o modelo User do admin e registrando o CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(EnvioMensagem)
class EnvioMensagemAdmin(admin.ModelAdmin):
    list_display = ('mensagem', 'data_envio', 'enviado', 'progresso', 'total_alunos')
    actions = ['enviar_mensagens']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('enviar-mensagem/<int:pk>/', self.admin_site.admin_view(self.enviar_mensagem)),  # Fechado corretamente
            path('verificar-progresso/<int:pk>/', self.admin_site.admin_view(self.verificar_progresso)),
        ]
        return custom_urls + urls
    
    def enviar_mensagem(self, request, pk):
        envio = EnvioMensagem.objects.get(pk=pk)
        alunos = Aluno.objects.filter(ativo=True)
        
        # Atualizar total de alunos
        envio.total_alunos = alunos.count()
        envio.save()
        
        return render(request, 'admin/envio_progresso.html', {
            'envio': envio,
        })
    
    def verificar_progresso(self, request, pk):
        envio = EnvioMensagem.objects.get(pk=pk)
        return JsonResponse({
            'progresso': envio.progresso,
            'total': envio.total_alunos,
            'enviado': envio.enviado,
        })
    
    def enviar_mensagens(self, request, queryset):
        for envio in queryset:
            if not envio.enviado:
                # Cria uma URL para iniciar o envio
                url = f'{request.path}enviar-mensagem/{envio.id}/'
                messages.info(request, f'<a href="{url}" target="_blank">Clique aqui para iniciar o envio da mensagem "{envio.mensagem}"</a>')
            else:
                messages.warning(request, f'A mensagem "{envio.mensagem}" já foi enviada')
    
    enviar_mensagens.short_description = "Enviar mensagens selecionadas"


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'curso', 'email', 'telefone', 'data_inscricao')
    list_filter = ('curso', 'provincia', 'municipio', 'data_inscricao', 'aceita_termos')
    search_fields = ('nome_completo', 'numero_bi', 'email', 'telefone')
    readonly_fields = ('data_inscricao', 'ip_address')

    fieldsets = (
        ('Informações Pessoais', {
            'fields': (
                'nome_completo', 'numero_bi', 'data_nascimento', 'idade',
                'data_emissao', 'genero', 'nacionalidade', 'copia_bi'
            )
        }),
        ('Documentos', {
            'fields': ('certificado', 'atestado_medico')
        }),
        ('Informações Acadêmicas', {
            'fields': ('curso', 'escola_anterior', 'ano_conclusao', 'endereco_escola')
        }),
        ('Informações de Contato', {
            'fields': ('telefone', 'email', 'provincia', 'municipio', 'endereco')
        }),
        ('Motivação', {
            'fields': ('motivacao', 'expectativas', 'planos_futuros')
        }),
        ('Termos e Consentimento', {
            'fields': ('aceita_termos', 'receber_informacoes')
        }),
        ('Metadados', {
            'fields': ('data_inscricao', 'ip_address')
        }),
    )
    
    


class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'duracao', 'destaque')  # Exibe essas colunas na lista de cursos
    search_fields = ('nome',)  # Permite buscar cursos pelo nome
    list_filter = ('destaque',)  # Permite filtrar cursos pelo status de destaque
    ordering = ('nome',)  # Ordena a lista de cursos pelo nome

admin.site.register(Curso, CursoAdmin)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data', 'local', 'horario_inicio', 'horario_fim')  # Exibindo esses campos na lista
    search_fields = ('nome', 'descricao')  # Permitindo pesquisa por nome e descrição
    list_filter = ('data',)  # Permitindo filtragem por data
    date_hierarchy = 'data'  # Adicionando uma hierarquia de datas

admin.site.register(Evento, EventoAdmin)
