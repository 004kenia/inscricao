from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.db import IntegrityError  
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.conf import settings
from hashlib import sha256
from datetime import datetime
import os
from django.shortcuts import render, get_object_or_404
from .models import Inscricao, Aluno, EnvioMensagem, Curso, Evento, Testimonial, Area



def login(request):
    status = request.GET.get('status')
    return render(request, 'login.html', {'status':status})

def cadastro(request):
    status = request.GET.get('status')
    return render(request, 'cadastro.html', {'status':status})

def trigger_404(request):
    raise Http404("Página não encontrada")

def erro_404_view(request, exception):
    return render(request, '404.html', status=404)


def eventos(request):
    eventos = Evento.objects.all() 
    return render(request, 'index.html', {'eventos': eventos})

def detalhe_evento(request, id):
    evento = get_object_or_404(Evento, id=id) 
    return render(request, 'detalhe_evento.html', {'evento': evento})

def detalhe_curso(request, id):
    curso = get_object_or_404(Curso, id=id)
    return render(request, 'detalhe.html', {'curso': curso})


def home(request):
    status = request.GET.get('status')
    curso = Curso.objects.all() 
    comentario = Testimonial.objects.all()
    eventos = Evento.objects.all()
    return render(request, "index.html", {'curso': curso, 'eventos':eventos, status:'status', 'comentario':comentario})

def admin(request):
    return render(request, 'admin.html')

def ficha(request):
    aluno_id = request.session.get('aluno', None)
    
    if not aluno_id:
        return redirect('/home?status=1')  
    aluno = Aluno.objects.get(id=aluno_id)
    nome_aluno = aluno.nome  
    
   
    if nome_aluno != 'Usuário':
        nome_parts = nome_aluno.split()
        if len(nome_parts) > 1:
            abreviacao = nome_parts[0][0] + nome_parts[-1][0] 
        else:
            abreviacao = nome_parts[0][0]  
    else:
        abreviacao = 'JS'  

    return render(request, 'ficha.html', {'nome_aluno': nome_aluno, 'abreviacao': abreviacao})


def valida_cadastro_aluno(request):
    nome = request.POST.get('nome')
    email = request.POST.get('email')  
    senha = request.POST.get('senha')

    aluno = Aluno.objects.filter(email=email)
    
    if not nome or not senha or len(nome.strip()) == 0 or len(senha.strip()) == 0:
        return redirect('/auth/cadastro/?status=1')
    
    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return redirect('/cadastro/?status=5')  
    
    if len(senha) < 8:
        return redirect('/auth/cadastro/?status=2')
    
    if aluno.exists():
        return redirect('/auth/cadastro/?status=3')
    
    try:
        senha_hash = sha256(senha.encode()).hexdigest()
        aluno = Aluno(nome=nome, email=email, senha=senha_hash)
        aluno.save()
        
        enviar_email_boas_vindas(nome, email)
        
        return redirect('/auth/cadastro/?status=0')
    
    except Exception as e:
        import traceback
        traceback.print_exc() 
        return redirect('/auth/cadastro/?status=4')


def enviar_email_boas_vindas(nome, email):
    assunto = "Bem-vindo ao IPIZ!"

    contexto = {
        'nome': nome,
        'plataforma': 'IPIZ',
        'cor_primaria': '#333333',
        'cor_secundaria': '#000000',
    }

    try:
        html_content = render_to_string('bem_vindo.html', contexto)
        text_content = strip_tags(html_content)

        email_msg = EmailMultiAlternatives(
            subject=assunto,
            body=text_content,
            from_email='danielkenia@gmail.com',  # Substitua por um e-mail válido
            to=[email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()
    except Exception as e:
        import traceback
        traceback.print_exc()
        

def valida_login_aluno(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    
    if not email or not senha:
        return redirect('/auth/login/?status=1')
    
    try:
        senha_hash = sha256(senha.encode()).hexdigest()
        aluno = Aluno.objects.get(email=email)
        
        if not aluno.ativo:
            return redirect('/auth/login/?status=2')
            
            
        request.session['aluno'] = aluno.id
        request.session['nome_aluno'] = aluno.nome
        return redirect('/auth/ficha?status=0')
        
    except Aluno.DoesNotExist:
        return redirect('/auth/login/?status=1')
    except Exception as e:
        return redirect('/auth/login/?status=3')
    
    



def calcular_idade(data_nascimento):
    hoje = datetime.now().date()
    return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))



def enviar_email_confirmacao(nome, curso, destinatario_email):
    try:
        assunto = f'Confirmação de Inscrição - {curso}'
        
        contexto = {
            'nome': nome,
            'curso': curso,
            'data': datetime.now().strftime('%d/%m/%Y'),
            'instituto': 'Instituto 17 de Dezembro'
        }

        
        html_message = render_to_string('email_inscricao_sucesso.html', contexto)
        
       
        text_message = strip_tags(html_message)

       
        email = EmailMultiAlternatives(
            subject=assunto,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario_email],
            reply_to=['nao-responda@educangola.com']
        )
        
        
        email.attach_alternative(html_message, "text/html")

     
        email.send(fail_silently=False)
        
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail de confirmação: {str(e)}")
        return False


def salvar_inscricao(request):
    if request.method == 'POST':
        try:
            required_files = ['copia_bi', 'certificado', 'atestado_medico']
            for file_field in required_files:
                if file_field not in request.FILES:
                    return JsonResponse({
                        'success': False,
                        'message': f'Por favor, envie o arquivo {file_field}'
                    }, status=400)

            fs = FileSystemStorage()
            bi_filename = fs.save(f'documentos/bi/{request.FILES["copia_bi"].name}', request.FILES['copia_bi'])
            cert_filename = fs.save(f'documentos/certificados/{request.FILES["certificado"].name}', request.FILES['certificado'])
            atestado_filename = fs.save(f'documentos/atestados/{request.FILES["atestado_medico"].name}', request.FILES['atestado_medico'])

            data_nascimento = datetime.strptime(request.POST['data_nascimento'], '%Y-%m-%d').date()
            data_emissao = datetime.strptime(request.POST['data_emissao'], '%Y-%m-%d').date()

            inscricao = Inscricao(
                copia_bi=bi_filename,
                nome_completo=request.POST['nome_completo'],
                numero_bi=request.POST['numero_bi'],
                data_nascimento=data_nascimento,
                idade=int(request.POST['idade']),
                data_emissao=data_emissao,
                genero=request.POST['genero'],
                nacionalidade=request.POST['nacionalidade'],
                certificado=cert_filename,
                atestado_medico=atestado_filename,
                curso=request.POST['curso'],
                escola_anterior=request.POST['escola_anterior'],
                ano_conclusao=int(request.POST['ano_conclusao']),
                endereco_escola=request.POST['endereco_escola'],
                telefone=request.POST['telefone'],
                email=request.POST['email'],
                provincia=request.POST['provincia'],
                municipio=request.POST['municipio'],
                endereco=request.POST['endereco'],
                motivacao=request.POST['motivacao'],
                expectativas=request.POST['expectativas'],
                planos_futuros=request.POST['planos_futuros'],
                aceita_termos='aceita_termos' in request.POST,
                receber_informacoes='receber_informacoes' in request.POST,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            inscricao.save()
            
            email_enviado = enviar_email_confirmacao(
                inscricao.nome_completo, 
                inscricao.get_curso_display(), 
                inscricao.email
            )

            return JsonResponse({
                'success': True,
                'message': 'Inscrição realizada com sucesso! Em breve você receberá um e-mail de confirmação.',
                'inscricao_id': inscricao.id
                
            })

        except Exception as e:
            print(f"Erro no processamento da inscrição: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Ocorreu um erro: {str(e)}'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)

    
        
def bem_vindo(request):
    return render(request, 'bem_vindo.html')



def cursos(request):
    curso = Curso.objects.all() 
    return render(request, 'index.html', {'curso': curso})


def termo(request):
    return render(request, 'termo.html')


def inscricao_detalhes(request, inscricao_id):
    try:
        inscricao = Inscricao.objects.get(id=inscricao_id)
        return render(request, 'detalhe_inscricao.html', {
            'inscricao': inscricao,
            'title': f'Inscrição #{inscricao.id}',
            'status': 'success'
        })
    except Inscricao.DoesNotExist:
        messages.error(request, 'Inscrição não encontrada')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro: {str(e)}')
        return redirect('home')
    
def professor(request):
    return render(request, 'professor.html')


def todos_cursos(request):
    areas = Area.objects.all()
    areas_com_cursos = []
    
    for area in areas:
        areas_com_cursos.append({
            'area': area,
            'cursos': Curso.objects.filter(area=area)
        })
    
    context = {
        'areas_com_cursos': areas_com_cursos
    }
    return render(request, 'cursos.html', context)


def lab(request):
    return render(request, 'lab.html')

def empresa(request):
    return render(request, 'empresa.html')


from django.shortcuts import render
from django.shortcuts import render
from django.db.models import Prefetch
from .models import Departamento, Docente, Disciplina

from django.shortcuts import render
from django.db.models import Prefetch
from .models import Departamento, Docente

def corpo_docente(request):
    # Debug inicial
    print("\n=== DEBUG INICIAL ===")
    print("Total de departamentos:", Departamento.objects.count())
    print("Departamentos ativos:", Departamento.objects.filter(ativo=True).count())
    print("Total de professores:", Docente.objects.count())
    print("Professores ativos:", Docente.objects.filter(ativo=True).count())

    # Query principal
    departamentos = Departamento.objects.filter(ativo=True).prefetch_related(
        Prefetch('docente_set', 
                queryset=Docente.objects.filter(ativo=True)
                .select_related('departamento')
                .prefetch_related('disciplinas')
        )
    ).order_by('nome')

    departamentos_data = []
    for dept in departamentos:
        professores = dept.docente_set.all()
        if professores.exists():
            departamentos_data.append({
                'obj': dept,
                'docentes': professores
            })
            print(f"Departamento '{dept.nome}' com {professores.count()} professores adicionado")

    # Fallback para professores sem departamento ou departamentos sem professores
    if not departamentos_data:
        professores_ativos = Docente.objects.filter(ativo=True)
        if professores_ativos.exists():
            print("\nAVISO: Usando fallback - mostrando todos os professores ativos")
            departamentos_data.append({
                'obj': type('', (), {
                    'nome': 'Todos os Professores',
                    'descricao': 'Lista de todos os professores ativos',
                    'slug': 'todos-professores'
                })(),
                'docentes': professores_ativos
            })
        else:
            print("\nAVISO: Nenhum professor ativo encontrado")

    context = {
        'departamentos_data': departamentos_data,
        'total_professores': sum(len(dept['docentes']) for dept in departamentos_data)
    }
    print(f"Final: {len(departamentos_data)} departamentos, {context['total_professores']} professores")
    return render(request, 'professor.html', context)


from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse

def docente_modal(request, docente_id):
    docente = get_object_or_404(
        Docente.objects.filter(ativo=True)
        .select_related('departamento')
        .prefetch_related(
            'disciplinas',
            Prefetch('formacao', queryset=FormacaoAcademica.objects.order_by('-ano_conclusao')),
            Prefetch('experiencia', queryset=ExperienciaProfissional.objects.order_by('-data_inicio')),
            'areas_pesquisa',
            Prefetch('publicacoes', queryset=Publicacao.objects.order_by('-ano'))
        ),
        id=docente_id
    )
    
    html = render_to_string('_docente_modal.html', {
        'docente': docente
    })
    
    return JsonResponse({'html': html})