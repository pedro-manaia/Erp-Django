import os
import random
from time import sleep

PROVIDER = os.getenv("FISCAL_PROVIDER", "mock")
API_KEY = os.getenv("FISCAL_API_KEY", "changeme")
ENV = os.getenv("FISCAL_ENV", "homologacao")

def send_document(payload: dict) -> dict:
    """Stub do provedor fiscal.
    Substituir por chamadas reais (PlugNotas, NFe.io etc.).
    """
    if PROVIDER == "mock":
        sleep(0.2)
        autorizado = random.choice([True, True, True, False])  # 75% de chance
        if autorizado:
            return {
                "status":"autorizada",
                "chave":"35140800000000000000550010000000011000000010",
                "numero": random.randint(1, 999999),
                "serie": 1,
                "xml":"<xml>...</xml>",
                "provider_id": f"mock-{random.randint(1000,9999)}"
            }
        else:
            return {"status":"rejeitada","motivo":"Rejeição simulada 999"}
    raise NotImplementedError(f"Provedor não implementado: {PROVIDER}")
