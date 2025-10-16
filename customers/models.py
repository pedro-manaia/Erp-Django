from django.db import models

class Customer(models.Model):
    PESSOA_TIPO = (
        ("F", "Física"),
        ("J", "Jurídica"),
    )
    tipo = models.CharField(max_length=1, choices=PESSOA_TIPO, default="J")
    nome = models.CharField(max_length=150)
    razao_social = models.CharField(max_length=150, blank=True)
    cpf_cnpj = models.CharField(max_length=18, unique=True)
    ie = models.CharField("Inscrição Estadual", max_length=20, blank=True)
    im = models.CharField("Inscrição Municipal", max_length=20, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)  # NOVO
    data_nascimento = models.DateField(null=True, blank=True)  # NOVO
    endereco = models.CharField(max_length=255, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    uf = models.CharField(max_length=2, blank=True)
    cep = models.CharField(max_length=10, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome or self.razao_social
