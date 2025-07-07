
from typing import List, Dict, Optional
from src.domain.entities import ValidatedTransaction, Address, TransferDetail
from src.application.interfaces import IValidatedTransactionRepository, IAddressRepository, IBlockchainService

# Esta camada contém os casos de uso (Use Cases), que representam a lógica de negócio específica da aplicação.
# Eles orquestram o fluxo de dados entre as entidades de domínio e as interfaces (portas) para serviços externos.
# Os casos de uso são independentes de frameworks e bancos de dados, dependendo apenas das interfaces.
# Isso adere ao Princípio da Responsabilidade Única (SRP) e ao Princípio Aberto/Fechado (OCP).

class ValidateTransactionUseCase:
    """Caso de uso para validar uma transação on-chain para fins de crédito.

    Este caso de uso encapsula a lógica de negócio para determinar se uma transação
    Ethereum é válida e segura para ser creditada. Ele utiliza os repositórios e
    serviços de blockchain através de suas interfaces, garantindo a Inversão de Dependência (D de SOLID).
    A lógica de validação é centralizada aqui, aderindo ao SRP.
    """

    def __init__(
        self,
        validated_tx_repository: IValidatedTransactionRepository,
        address_repository: IAddressRepository,
        blockchain_service: IBlockchainService,
    ):
        """
        Inicializa o caso de uso com as dependências necessárias.

        Args:
            validated_tx_repository (IValidatedTransactionRepository): Repositório para persistir transações validadas.
            address_repository (IAddressRepository): Repositório para consultar endereços próprios.
            blockchain_service (IBlockchainService): Serviço para interagir com a blockchain.
        """
        self.validated_tx_repository = validated_tx_repository
        self.address_repository = address_repository
        self.blockchain_service = blockchain_service

    def execute(self, tx_hash: str) -> Dict:
        """
        Executa a validação de uma transação.

        Args:
            tx_hash (str): O hash da transação a ser validada.

        Returns:
            Dict: Um dicionário contendo o resultado da validação.
        
        Raises:
            ValueError: Se o hash da transação for inválido ou a transação não for encontrada.
        """
        if not tx_hash:
            raise ValueError("Hash da transação é obrigatório.")

        # Verifica se a transação já foi validada e salva para evitar duplicação (SRP).
        existing_validation = self.validated_tx_repository.find_by_hash(tx_hash)
        if existing_validation:
            return {
                "status": "success",
                "message": "Transação já validada anteriormente.",
                "validation_result": {
                    "is_valid": existing_validation.is_valid,
                    "asset": existing_validation.asset,
                    "to_address": existing_validation.to_address,
                    "value": existing_validation.value,
                },
            }

        tx_details = self.blockchain_service.get_transaction_details(tx_hash)
        tx_receipt = self.blockchain_service.get_transaction_receipt(tx_hash)

        if not tx_details or not tx_receipt:
            raise ValueError("Transação não encontrada ou pendente.")

        asset = "ETH"
        transfers: List[TransferDetail] = []

        # Identificar se é tx de ETH ou token ERC-20
        if tx_details.get("value", 0) > 0 and not tx_details.get("input", b"").startswith(b"0x"): # Transação ETH simples
            transfers.append(
                TransferDetail(
                    asset="ETH",
                    to_address=tx_details["to"],
                    value=str(tx_details["value"])
                )
            )

        # Para transações de token ERC-20 (verificar logs)
        for log in tx_receipt.get("logs", []):
            decoded_log = self.blockchain_service.decode_erc20_transfer_log(log)
            if decoded_log:
                transfers.append(decoded_log)
                asset = decoded_log.asset # Atualiza o ativo principal se for ERC-20

        # Confirmar se o destino da transferência é um de nossos endereços gerados
        is_destination_our_address = False
        our_addresses = [addr.address for addr in self.address_repository.get_all()]

        for transfer in transfers:
            if transfer.to_address in our_addresses:
                is_destination_our_address = True
                break

        # Se a transação é válida e segura para gerar crédito.
        is_valid_and_safe = False
        if tx_receipt.get("status") == 1:
            current_block = self.blockchain_service.get_current_block_number()
            confirmations = current_block - tx_receipt.get("blockNumber", 0)

            MIN_CONFIRMATIONS = 12

            if confirmations >= MIN_CONFIRMATIONS and is_destination_our_address:
                is_valid_and_safe = True

        response_data = {
            "tx_hash": tx_hash,
            "is_valid_and_safe_for_credit": is_valid_and_safe,
            "transfers": [t.__dict__ for t in transfers],
            "confirmations": confirmations if "confirmations" in locals() else 0,
            "tx_status": "success" if tx_receipt.get("status") == 1 else "failed",
        }

        # Armazenar as transações válidas em uma base de dados para consulta do histórico.
        if is_valid_and_safe:
            new_validated_tx = ValidatedTransaction(
                tx_hash=tx_hash,
                asset=asset,
                to_address=transfers[0].to_address if transfers else "N/A",
                value=str(transfers[0].value) if transfers else "0",
                is_valid=True,
            )
            self.validated_tx_repository.save(new_validated_tx)

        return response_data


