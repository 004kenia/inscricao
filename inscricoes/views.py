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
from .models import Inscricao, Aluno, EnvioMensagem, Curso, Evento, Testimonial



def eventos(request):
    eventos = Evento.objects.all()  # Obtém todos os eventos
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
        return redirect('/?status=1')
    
    if len(senha) < 8:
        return redirect('/?status=2')
    
    if aluno.exists():
        return redirect('/?status=3')
    
    try:
        senha_hash = sha256(senha.encode()).hexdigest()
        aluno = Aluno(nome=nome, email=email, senha=senha_hash)
        aluno.save()
        
       
        enviar_email_boas_vindas(nome, email)
        
        return redirect('/?status=0')
    
    except Exception as e:
        print(f"Erro ao cadastrar aluno: {e}")
        return redirect('/?status=4')

def enviar_email_boas_vindas(nome, email):
    assunto = "Bem-vindo ao IPIZ!"
    
    contexto = {
        'nome': nome,
        'plataforma': 'IPIZ',
        'cor_primaria': '#333333',  
        'cor_secundaria': '#000000',  
    }
    
    html_content = render_to_string('bem_vindo.html', contexto)
    text_content = strip_tags(html_content)
    
    email_msg = EmailMultiAlternatives(
        subject=assunto,
        body=text_content,
        from_email='nao-responda@educangola.com',
        to=[email],
    )
    email_msg.attach_alternative(html_content, "text/html")
    
    try:
        email_msg.send()
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def valida_login_aluno(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    
    if not email or not senha:
        return redirect('/?status=1')
    
    try:
        senha_hash = sha256(senha.encode()).hexdigest()
        aluno = Aluno.objects.get(email=email)
        
        if not aluno.ativo:
            return redirect('/?status=2')
            
            
        request.session['aluno'] = aluno.id
        request.session['nome_aluno'] = aluno.nome
        return redirect('/auth/ficha?status=0')
        
    except Aluno.DoesNotExist:
        return redirect('/?status=1')
    except Exception as e:
        return redirect('/?status=3')
    
    



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

            if not email_enviado:
                print("Aviso: E-mail de confirmação não foi enviado, mas a inscrição foi salva")

            return JsonResponse({
                'success': True,
                'message': 'Inscrição realizada com sucesso!',
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

