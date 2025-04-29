from celery import shared_task

@shared_task
def enviar_email_em_massa(envio_id):
    envio = EnvioMensagem.objects.get(id=envio_id)
    envio.enviar_email_para_alunos()