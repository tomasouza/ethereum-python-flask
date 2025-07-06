
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import Address, ValidatedTransaction, CreatedTransaction, TransferDetail

# Esta camada define as interfaces (portas) que a camada de aplicação (Use Cases) utiliza.
# Ela é crucial para o Princípio da Inversão de Dependência (D de SOLID), garantindo que
# as regras de negócio de alto nível não dependam de detalhes de implementação de baixo nível.
# Em vez disso, ambas dependem de abstrações (estas interfaces).

# --- Interfaces de Repositório ---
# Estas interfaces definem os contratos para operações de persistência de dados.
# Elas permitem que a camada de aplicação interaja com o armazenamento de dados
# sem conhecer os detalhes de como os dados são realmente persistidos (ex: SQLAlchemy, MongoDB).
# Isso adere ao Princípio da Segregação de Interfaces (I de SOLID), pois cada interface
# é específica para um tipo de entidade e suas operações.

class IAddressRepository(ABC):
    """Interface para o repositório de endereços.
    Define as operações CRUD (Create, Read, Update, Delete) para a entidade Address.
    """
    @abstractmethod
    def save(self, address: Address) -> Address:
        pass

    @abstractmethod
    def find_by_address(self, address: str) -> Optional[Address]:
        pass

    @abstractmethod
    def get_all(self) -> List[Address]:
        pass

class IValidatedTransactionRepository(ABC):
    """Interface para o repositório de transações validadas.
    Define as operações para persistir e consultar transações que foram validadas.
    """
    @abstractmethod
    def save(self, tx: ValidatedTransaction) -> ValidatedTransaction:
        pass

    @abstractmethod
    def find_by_hash(self, tx_hash: str) -> Optional[ValidatedTransaction]:
        pass

    @abstractmethod
    def get_all(self) -> List[ValidatedTransaction]:
        pass

class ICreatedTransactionRepository(ABC):
    """Interface para o repositório de transações criadas.
    Define as operações para persistir, consultar e atualizar transações que foram iniciadas pela aplicação.
    """
    @abstractmethod
    def save(self, tx: CreatedTransaction) -> CreatedTransaction:
        pass

    @abstractmethod
    def find_by_hash(self, tx_hash: str) -> Optional[CreatedTransaction]:
        pass

    @abstractmethod
    def get_all(self) -> List[CreatedTransaction]:
        pass

    @abstractmethod
    def update(self, tx: CreatedTransaction) -> CreatedTransaction:
        pass

# --- Interface de Serviço de Blockchain ---
# Esta interface define o contrato para interações com a rede blockchain.
# Ela abstrai os detalhes de implementação da biblioteca Web3.py ou de qualquer outro
# provedor de blockchain, permitindo que a camada de aplicação seja independente da tecnologia.
# Isso também adere ao Princípio da Segregação de Interfaces (I de SOLID).

class IBlockchainService(ABC):
    """Interface para o serviço que interage com a blockchain.
    Define as operações necessárias para gerar endereços, consultar transações e enviar transações.
    """
    @abstractmethod
    def generate_new_address(self) -> Address:
        pass

    @abstractmethod
    def get_transaction_details(self, tx_hash: str) -> dict:
        pass

    @abstractmethod
    def get_transaction_receipt(self, tx_hash: str) -> dict:
        pass

    @abstractmethod
    def get_current_block_number(self) -> int:
        pass

    @abstractmethod
    def decode_erc20_transfer_log(self, log: dict) -> Optional[TransferDetail]:
        pass

    @abstractmethod
    def create_and_sign_transaction(
        self, from_address: str, to_address: str, asset: str, value: str, private_key: str
    ) -> tuple[str, dict]:
        pass

    @abstractmethod
    def send_raw_transaction(self, raw_tx: str) -> str:
        pass


