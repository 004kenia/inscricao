# Generated by Django 5.2 on 2025-05-02 15:18

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscricoes', '0009_testimonial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlunoA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome Completo')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='E-mail')),
                ('senha', models.CharField(max_length=128, verbose_name='Senha')),
                ('data_cadastro', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data de Cadastro')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'verbose_name': 'Aluno',
                'verbose_name_plural': 'Alunos',
            },
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='numero_bi',
            field=models.CharField(max_length=14, unique=True, verbose_name='Número do BI'),
        ),
    ]
