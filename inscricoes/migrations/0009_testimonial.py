# Generated by Django 5.2 on 2025-04-30 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscricoes', '0008_evento'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nome do cliente')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='testimonials/', verbose_name='Foto do cliente')),
                ('message', models.TextField(verbose_name='Depoimento')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
        ),
    ]
