
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

# Esta camada contém as entidades de domínio, que são o coração da aplicação.
# Elas encapsulam as regras de negócio mais importantes e são independentes de qualquer tecnologia externa.
# Este é o centro da Clean Architecture, garantindo que as regras de negócio permaneçam puras e testáveis.

@dataclass
class Address:
    """Representa um endereço Ethereum e sua chave privada associada.
    
    Esta entidade é fundamental para a funcionalidade de geração e gerenciamento de endereços.
    Em um contexto de produção, a `private_key` seria tratada com criptografia robusta ou
    gerenciada por um serviço de segredos externo para máxima segurança.
    """
    address: str
    private_key: str  # Em produção, esta chave deve ser criptografada ou gerenciada externamente.
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ValidatedTransaction:
    """Representa uma transação validada como segura para crédito.
    
    Esta entidade armazena os detalhes de transações que passaram por um processo de validação
    e são consideradas confiáveis para serem creditadas ao usuário. Ela reflete a regra de negócio
    de que apenas transações seguras devem ser processadas.
    """
    tx_hash: str
    asset: str  # Ex: 'ETH', 'USDT'
    to_address: str
    value: str  # Armazenar como string para evitar problemas de precisão com floats
    is_valid: bool
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CreatedTransaction:
    """Representa uma transação criada pela aplicação.
    
    Esta entidade rastreia as transações que foram iniciadas e enviadas pela própria aplicação.
    Ela contém informações sobre o status da transação e detalhes de custo, permitindo o monitoramento
    e a auditoria das operações de saída.
    """
    from_address: str
    to_address: str
    asset: str
    value: str
    status: str  # Ex: 'pending', 'confirmed', 'failed'
    tx_hash: Optional[str] = None  # Pode ser nulo até a transação ser enviada
    gas_price_gwei: Optional[str] = None
    gas_limit: Optional[int] = None
    effective_cost_wei: Optional[str] = None
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TransferDetail:
    """Representa os detalhes de uma transferência dentro de uma transação.
    
    Esta entidade auxiliar é usada para encapsular informações sobre transferências de ativos
    identificadas dentro de uma transação maior, como em logs de eventos ERC-20.
    """
    asset: str
    to_address: str
    value: str


