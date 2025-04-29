from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class Aluno(models.Model):
    nome = models.CharField(_('Nome Completo'), max_length=100)
    email = models.EmailField(_('E-mail'), unique=True)
    senha = models.CharField(_('Senha'), max_length=128)
    data_cadastro = models.DateTimeField(_('Data de Cadastro'), default=timezone.now)
    ativo = models.BooleanField(_('Ativo'), default=True)
    
    def __str__(self):
        return f"Aluno: {self.nome}"

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        

class PerfilAluno(models.Model):
    aluno = models.OneToOneField('Aluno', on_delete=models.CASCADE, related_name='perfil')
    imagem = models.ImageField(_('Imagem de Perfil'), upload_to='perfil_alunos/', null=True, blank=True)
    biografia = models.TextField(_('Biografia'), blank=True)
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True, null=True)
    github = models.URLField(_('GitHub'), blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Perfil de {self.aluno.nome}"

    class Meta:
        verbose_name = 'Perfil do Aluno'
        verbose_name_plural = 'Perfis dos Alunos'
        
        


from django.db import models
from django.core.validators import FileExtensionValidator

class Inscricao(models.Model):
    # Informações Pessoais
    copia_bi = models.FileField(
        upload_to='documentos/bi/',
        validators=[FileExtensionValidator(['pdf'])],
        verbose_name='Cópia do BI'
    )
    nome_completo = models.CharField(max_length=200, verbose_name='Nome Completo')
    numero_bi = models.CharField(max_length=14, verbose_name='Número do BI')
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    idade = models.PositiveIntegerField(verbose_name='Idade')
    data_emissao = models.DateField(verbose_name='Data de Emissão do BI')
    genero = models.CharField(
        max_length=10,
        choices=[('masculino', 'Masculino'), ('feminino', 'Feminino')],
        verbose_name='Gênero'
    )
    nacionalidade = models.CharField(max_length=100, verbose_name='Nacionalidade')
    
    # Documentos
    certificado = models.FileField(
        upload_to='documentos/certificados/',
        validators=[FileExtensionValidator(['pdf'])],
        verbose_name='Certificado da 9ª Classe'
    )
    atestado_medico = models.FileField(
        upload_to='documentos/atestados/',
        validators=[FileExtensionValidator(['pdf'])],
        verbose_name='Atestado Médico'
    )
    
    # Informações Acadêmicas
    curso = models.CharField(
        max_length=50,
        choices=[
            ('electrotecnica', 'Electrotécnica'),
            ('mecanica', 'Mecânica Industrial'),
            ('informatica', 'Informática Industrial')
        ],
        verbose_name='Curso Selecionado'
    )
    escola_anterior = models.CharField(max_length=200, verbose_name='Escola Anterior')
    ano_conclusao = models.PositiveIntegerField(verbose_name='Ano de Conclusão')
    endereco_escola = models.CharField(max_length=300, verbose_name='Endereço da Escola')
    
    # Informações de Contato
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    email = models.EmailField(verbose_name='Email')
    provincia = models.CharField(max_length=50, verbose_name='Província')
    municipio = models.CharField(max_length=50, verbose_name='Município')
    endereco = models.CharField(max_length=300, verbose_name='Endereço Completo')
    
    # Motivação
    motivacao = models.TextField(verbose_name='Motivação para o Curso')
    expectativas = models.TextField(verbose_name='Expectativas em relação ao Curso')
    planos_futuros = models.TextField(verbose_name='Planos Futuros')
    
    # Termos e Condições
    aceita_termos = models.BooleanField(verbose_name='Aceita os Termos e Condições')
    receber_informacoes = models.BooleanField(
        default=False,
        verbose_name='Deseja receber informações'
    )
    
    # Metadados
    data_inscricao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Inscrição')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Endereço IP')
    
    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        ordering = ['-data_inscricao']
    
    def __str__(self):
        return f'{self.nome_completo} - {self.curso}'
    
class EnvioMensagem(models.Model):
    mensagem = models.TextField(_('Mensagem'))
    data_envio = models.DateTimeField(_('Data de Envio'), default=timezone.now)
    enviado = models.BooleanField(_('Enviado'), default=False)
    progresso = models.IntegerField(_('Progresso'), default=0)
    total_alunos = models.IntegerField(_('Total de Alunos'), default=0)
    alunos_enviados = models.ManyToManyField('Aluno', related_name='envios', blank=True)
    
    def __str__(self):
        return f"Envio de mensagem ({self.progresso}/{self.total_alunos})"
    
    class Meta:
        verbose_name = 'Envio de Mensagem'
        verbose_name_plural = 'Envios de Mensagens'
        
        
class Curso(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome do Curso")
    descricao = models.TextField(verbose_name="Descrição do Curso")
    duracao = models.CharField(max_length=50, verbose_name="Duração")
    imagem = models.ImageField(upload_to='cursos/', verbose_name="Imagem do Curso")
    destaque = models.BooleanField(default=False, verbose_name="Destaque (Novo/Popular)")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        
        
class Evento(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome do Evento")
    descricao = models.TextField(verbose_name="Descrição do Evento")
    data = models.DateField(verbose_name="Data do Evento")
    horario_inicio = models.TimeField(verbose_name="Hora de Início")
    horario_fim = models.TimeField(verbose_name="Hora de Fim")
    local = models.CharField(max_length=255, verbose_name="Local do Evento")
    imagem = models.ImageField(upload_to='eventos/', verbose_name="Imagem do Evento")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'