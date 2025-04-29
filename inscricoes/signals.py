# inscricoes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EnvioMensagem
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=EnvioMensagem)
def enviar_email_envio_mensagem(sender, instance, created, **kwargs):
    if created and not instance.enviado:
        # Aqui você pode ajustar o que será enviado para os alunos
        # Enviar para todos os alunos que estão na ManyToManyField
        for aluno in instance.alunos_enviados.all():
            send_mail(
                subject="Nova Mensagem",
                message=instance.mensagem,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[aluno.email],  # Supondo que o modelo `Aluno` tenha um campo `email`
                fail_silently=False,
            )
            # Atualizar o campo `enviado` após o envio do e-mail
        instance.enviado = True
        instance.save()  # Salvando a instância após marcar como enviado
