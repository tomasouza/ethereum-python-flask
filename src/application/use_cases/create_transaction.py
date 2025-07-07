
from typing import Optional
from src.domain.entities import CreatedTransaction
from src.application.interfaces import ICreatedTransactionRepository, IAddressRepository, IBlockchainService

# Esta camada contém os casos de uso (Use Cases), que representam a lógica de negócio específica da aplicação.
# Eles orquestram o fluxo de dados entre as entidades de domínio e as interfaces (portas) para serviços externos.
# Os casos de uso são independentes de frameworks e bancos de dados, dependendo apenas das interfaces.
# Isso adere ao Princípio da Responsabilidade Única (SRP) e ao Princípio Aberto/Fechado (OCP).

class CreateTransactionUseCase:
    """Caso de uso para criar e enviar uma transação on-chain.

    Este caso de uso coordena o processo de criação e envio de uma transação.
    Ele depende das abstrações `ICreatedTransactionRepository`, `IAddressRepository` e `IBlockchainService`,
    demonstrando o Princípio da Inversão de Dependência (D de SOLID).
    Sua responsabilidade é orquestrar a operação, não lidar com os detalhes de persistência ou interação com a blockchain.
    """

    def __init__(
        self,
        created_tx_repository: ICreatedTransactionRepository,
        address_repository: IAddressRepository,
        blockchain_service: IBlockchainService,
    ):
        """
        Inicializa o caso de uso com as dependências necessárias.

        Args:
            created_tx_repository (ICreatedTransactionRepository): Repositório para persistir transações criadas.
            address_repository (IAddressRepository): Repositório para consultar endereços próprios.
            blockchain_service (IBlockchainService): Serviço para interagir com a blockchain.
        """
        self.created_tx_repository = created_tx_repository
        self.address_repository = address_repository
        self.blockchain_service = blockchain_service

    def execute(
        self, from_address: str, to_address: str, asset: str, value: str
    ) -> CreatedTransaction:
        """
        Executa a criação e envio de uma transação.

        Args:
            from_address (str): Endereço de origem do saldo.
            to_address (str): Endereço de destino da transferência.
            asset (str): Ativo a ser transferido (
                'ETH' ou endereço do contrato ERC-20
            ).
            value (str): Valor da transferência em formato decimal.

        Returns:
            CreatedTransaction: A entidade da transação criada e enviada.
        
        Raises:
            ValueError: Se os campos obrigatórios não forem fornecidos ou o endereço de origem não for encontrado.
        """
        if not all([from_address, to_address, asset, value]):
            raise ValueError("Todos os campos (from_address, to_address, asset, value) são obrigatórios.")

        sender_account_db = self.address_repository.find_by_address(from_address)
        if not sender_account_db:
            raise ValueError("Endereço de origem não encontrado em nossa base de dados.")

        private_key = sender_account_db.private_key

        # Armazenar histórico da transação como 'pending' antes de enviar.
        # A responsabilidade de persistência é do repositório (SRP).
        new_created_tx = CreatedTransaction(
            from_address=from_address,
            to_address=to_address,
            asset=asset,
            value=value,
            status="pending",
        )
        self.created_tx_repository.save(new_created_tx)

        # Cria e envia a transação via serviço de blockchain (SRP).
        # O caso de uso não se preocupa com os detalhes de como a transação é assinada ou enviada.
        signed_raw_transacion, tx_details = self.blockchain_service.create_and_sign_transaction(
            from_address, to_address, asset, value, private_key
        )

        tx_hash = self.blockchain_service.send_raw_transaction(signed_raw_transacion)

        # Atualiza o hash da transação e detalhes de gás no banco de dados.
        # A responsabilidade de atualização é do repositório (SRP).
        new_created_tx.tx_hash = tx_hash
        new_created_tx.gas_price_gwei = str(tx_details.get("gasPrice", 0))
        new_created_tx.gas_limit = tx_details.get("gas", 0)
        self.created_tx_repository.update(new_created_tx)

        return new_created_tx

class UpdateTransactionStatusUseCase:
    """Caso de uso para atualizar o status de uma transação criada.

    Este caso de uso é responsável por consultar o status de uma transação na blockchain
    e atualizar o registro correspondente no banco de dados. Ele também adere ao SRP e DIP,
    dependendo das abstrações de repositório e serviço de blockchain.
    """

    def __init__(
        self,
        created_tx_repository: ICreatedTransactionRepository,
        blockchain_service: IBlockchainService,
    ):
        """
        Inicializa o caso de uso com as dependências necessárias.

        Args:
            created_tx_repository (ICreatedTransactionRepository): Repositório para persistir transações criadas.
            blockchain_service (IBlockchainService): Serviço para interagir com a blockchain.
        """
        self.created_tx_repository = created_tx_repository
        self.blockchain_service = blockchain_service

    def execute(self, tx_hash: str) -> CreatedTransaction:
        """
        Atualiza o status de uma transação no banco de dados com base no seu status na blockchain.

        Args:
            tx_hash (str): O hash da transação a ser atualizada.

        Returns:
            CreatedTransaction: A entidade da transação atualizada.
        
        Raises:
            ValueError: Se a transação não for encontrada.
        """
        tx_record = self.created_tx_repository.find_by_hash(tx_hash)
        if not tx_record:
            raise ValueError("Transação não encontrada.")

        tx_receipt = self.blockchain_service.get_transaction_receipt(tx_hash)
        if tx_receipt:
            if tx_receipt.get("status") == 1:
                tx_record.status = "confirmed"
                tx_record.effective_cost_wei = str(
                    tx_receipt.get("gasUsed", 0) * tx_receipt.get("effectiveGasPrice", 0)
                )
            else:
                tx_record.status = "failed"
            self.created_tx_repository.update(tx_record)
        else:
            tx_record.status = "pending" # Ainda pendente na rede

        return tx_record


