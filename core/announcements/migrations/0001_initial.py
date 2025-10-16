from django.db import migrations, models
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Mensagem')),
                ('level', models.CharField(choices=[('info', 'Informação (verde)'), ('warn', 'Cuidado (amarelo)'), ('alert', 'Atenção (vermelho)')], default='info', max_length=10, verbose_name='Nível')),
                ('active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Expira em')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Aviso',
                'verbose_name_plural': 'Avisos',
                'ordering': ['-created_at'],
            },
        ),
    ]
