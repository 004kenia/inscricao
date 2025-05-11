from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db import models

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
    numero_bi = models.CharField(max_length=14, verbose_name='Número do BI', unique=True)
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    idade = models.PositiveIntegerField(verbose_name='Idade')
    data_emissao = models.DateField(verbose_name='Data de Emissão do BI')
    genero = models.CharField(
        max_length=10,
        choices=[('masculino', 'Masculino'), ('feminino', 'Feminino')],
        verbose_name='Gênero'
    )
    nacionalidade = models.CharField(max_length=100, verbose_name='Nacionalidade')
    
    
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
    
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

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

    def enviar_email_para_alunos(self):
        """
        Função para enviar e-mail para todos os alunos que ainda não receberam a mensagem.
        """
        # Primeiro, obtenha todos os alunos cadastrados
        todos_alunos = Aluno.objects.all()
        self.total_alunos = todos_alunos.count()  # Atualiza o total de alunos
        
        # Obtenha os alunos que já receberam a mensagem
        alunos_enviados = self.alunos_enviados.all()
        
        # Filtre os alunos que ainda não receberam a mensagem
        alunos_para_enviar = todos_alunos.exclude(id__in=alunos_enviados.values_list('id', flat=True))
        
        # Para cada aluno que ainda não recebeu a mensagem
        for aluno in alunos_para_enviar:
            if aluno.email:  # Verifique se o aluno tem um e-mail
                try:
                    send_mail(
                        subject="Nova Mensagem",  # Assunto do e-mail
                        message=self.mensagem,  # Corpo da mensagem
                        from_email=settings.EMAIL_HOST_USER,  # Remetente
                        recipient_list=[aluno.email],  # Destinatário
                        fail_silently=False,
                    )
                    # Adiciona o aluno à lista de enviados
                    self.alunos_enviados.add(aluno)
                    self.progresso += 1  # Atualiza o progresso
                    self.save()  # Salva após cada envio para manter o progresso
                except Exception as e:
                    # Log do erro de envio
                    print(f"Erro ao enviar para {aluno.email}: {e}")
                    # Você pode querer continuar tentando enviar para os outros
                    continue
        
        # Verifica se todos os e-mails foram enviados
        if self.progresso >= self.total_alunos:
            self.enviado = True
            self.save()


        
class Area(models.Model):
    nome = models.CharField(max_length=255, verbose_name="Nome da Área")
    descricao = models.TextField(verbose_name="Descrição da Área", blank=True, null=True)
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

class Curso(models.Model):
    area = models.ForeignKey(
        Area, 
        on_delete=models.SET_NULL, 
        verbose_name="Área do Curso",
        null=True,
        blank=True
    )
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


class Testimonial(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome do cliente")
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, verbose_name="Foto do cliente")
    message = models.TextField(verbose_name="Depoimento")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    def __str__(self):
        return f"{self.name} - {self.message[:30]}"
    

class professor(models.Model):
    nome = models.CharField(_('Nome Completo'), max_length=100)
    email = models.EmailField(_('E-mail'), unique=True)
    senha = models.CharField(_('Senha'), max_length=128)
    data_cadastro = models.DateTimeField(_('Data de Cadastro'), default=timezone.now)
    bio = models.TextField()
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, null=True)
    
    
    def __str__(self):
        return f" professor: {self.nome}"


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Departamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    icone = models.CharField(max_length=50, blank=True, null=True)  
    
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, blank=True, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    carga_horaria = models.PositiveIntegerField()
    descricao = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ['nome']
        unique_together = ['nome', 'departamento']
    
    def __str__(self):
        return f"{self.nome} ({self.departamento})"

class FormacaoAcademica(models.Model):
    GRAU_CHOICES = [
        ('GR', 'Graduação'),
        ('ES', 'Especialização'),
        ('ME', 'Mestrado'),
        ('DO', 'Doutorado'),
        ('PD', 'Pós-Doutorado'),
    ]
    
    grau = models.CharField(max_length=2, choices=GRAU_CHOICES)
    curso = models.CharField(max_length=100)
    instituicao = models.CharField(max_length=100)
    ano_conclusao = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)
        ]
    )
    descricao = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Formação Acadêmica"
        verbose_name_plural = "Formações Acadêmicas"
        ordering = ['-ano_conclusao', 'grau']
    
    def __str__(self):
        return f"{self.get_grau_display()} em {self.curso} - {self.instituicao} ({self.ano_conclusao})"

class ExperienciaProfissional(models.Model):
    cargo = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)  # Null significa que ainda trabalha lá
    descricao = models.TextField(blank=True, null=True)
    atual = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Experiência Profissional"
        verbose_name_plural = "Experiências Profissionais"
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.cargo} na {self.empresa}"

class AreaPesquisa(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Área de Pesquisa"
        verbose_name_plural = "Áreas de Pesquisa"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Publicacao(models.Model):
    TIPO_CHOICES = [
        ('AR', 'Artigo'),
        ('LI', 'Livro'),
        ('CP', 'Capítulo de Livro'),
        ('TR', 'Trabalho em Conferência'),
        ('OU', 'Outro'),
    ]
    
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES)
    autores = models.CharField(max_length=300)
    veiculo = models.CharField(max_length=100)  
    ano = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)
        ]
    )
    link = models.URLField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Publicação"
        verbose_name_plural = "Publicações"
        ordering = ['-ano', 'titulo']
    
    def __str__(self):
        return f"{self.titulo} ({self.ano})"

class Docente(models.Model):
    CARGO_CHOICES = [
        ('PR', 'Professor'),
        ('CO', 'Coordenador'),
        ('DC', 'Diretor de Curso'),
        ('DP', 'Diretor de Departamento'),
    ]
    
    NIVEL_CHOICES = [
        ('AS', 'Assistente'),
        ('AD', 'Adjunto'),
        ('TI', 'Titular'),
        ('VI', 'Visitante'),
    ]
    
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='docentes/', blank=True, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=2, choices=CARGO_CHOICES, default='PR')
    nivel = models.CharField(max_length=2, choices=NIVEL_CHOICES, default='AS')
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True, null=True)
    lattes = models.URLField(blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)
    
    disciplinas = models.ManyToManyField(Disciplina, blank=True)
    formacao = models.ManyToManyField(FormacaoAcademica, blank=True)
    experiencia = models.ManyToManyField(ExperienciaProfissional, blank=True)
    areas_pesquisa = models.ManyToManyField(AreaPesquisa, blank=True)
    publicacoes = models.ManyToManyField(Publicacao, blank=True)
    
    horario_atendimento = models.TextField(blank=True, null=True)
    
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_cargo_display()})"
    
    @property
    def coordenador_departamento(self):
        return self.cargo == 'DP' or self.cargo == 'CO'
    
    def get_disciplinas_str(self):
        return ", ".join([d.nome for d in self.disciplinas.all()])
    
    def get_areas_pesquisa_str(self):
        return ", ".join([a.nome for a in self.areas_pesquisa.all()])