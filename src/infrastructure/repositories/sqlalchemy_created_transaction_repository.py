
from typing import List, Optional
from src.domain.entities import CreatedTransaction
from src.application.interfaces import ICreatedTransactionRepository
from src.infrastructure.database.models import db, CreatedTransactionModel

# Esta camada contém as implementações concretas das interfaces de repositório.
# Ela é responsável por lidar com os detalhes de persistência de dados, como a interação com o banco de dados.
# Aderindo ao Princípio da Inversão de Dependência (D de SOLID), esta classe implementa a interface
# `ICreatedTransactionRepository` definida na camada de aplicação, sem que a camada de aplicação precise conhecer
# os detalhes de como os dados são armazenados (neste caso, via SQLAlchemy).
# Também adere ao Princípio da Responsabilidade Única (SRP), sendo responsável apenas pela persistência de transações criadas.

class SQLAlchemyCreatedTransactionRepository(ICreatedTransactionRepository):
    """Implementação do repositório de transações criadas usando SQLAlchemy.

    Esta classe traduz as operações de domínio (definidas em `ICreatedTransactionRepository`)
    para operações específicas do SQLAlchemy, interagindo com o `CreatedTransactionModel`.
    """

    def save(self, tx: CreatedTransaction) -> CreatedTransaction:
        """Salva uma nova transação criada no banco de dados.

        Args:
            tx (CreatedTransaction): A entidade CreatedTransaction a ser salva.

        Returns:
            CreatedTransaction: A entidade CreatedTransaction salva, com o ID gerado pelo banco de dados.
        """
        new_tx_model = CreatedTransactionModel(
            tx_hash=tx.tx_hash,
            from_address=tx.from_address,
            to_address=tx.to_address,
            asset=tx.asset,
            value=tx.value,
            status=tx.status,
            gas_price_gwei=tx.gas_price_gwei,
            gas_limit=tx.gas_limit,
            effective_cost_wei=tx.effective_cost_wei,
            created_at=tx.created_at
        )
        db.session.add(new_tx_model)
        db.session.commit()
        tx.id = new_tx_model.id
        return tx

    def find_by_hash(self, tx_hash: str) -> Optional[CreatedTransaction]:
        """Busca uma transação criada pelo seu hash.

        Args:
            tx_hash (str): O hash da transação a ser buscada.

        Returns:
            Optional[CreatedTransaction]: A entidade CreatedTransaction encontrada, ou None se não existir.
        """
        tx_model = CreatedTransactionModel.query.filter_by(tx_hash=tx_hash).first()
        if tx_model:
            return CreatedTransaction(
                id=tx_model.id,
                tx_hash=tx_model.tx_hash,
                from_address=tx_model.from_address,
                to_address=tx_model.to_address,
                asset=tx_model.asset,
                value=tx_model.value,
                status=tx_model.status,
                gas_price_gwei=tx_model.gas_price_gwei,
                gas_limit=tx_model.gas_limit,
                effective_cost_wei=tx_model.effective_cost_wei,
                created_at=tx_model.created_at
            )
        return None

    def get_all(self) -> List[CreatedTransaction]:
        """Retorna todas as transações criadas armazenadas.

        Returns:
            List[CreatedTransaction]: Uma lista de todas as entidades CreatedTransaction no banco de dados.
        """
        tx_models = CreatedTransactionModel.query.all()
        return [
            CreatedTransaction(
                id=tx.id,
                tx_hash=tx.tx_hash,
                from_address=tx.from_address,
                to_address=tx.to_address,
                asset=tx.asset,
                value=tx.value,
                status=tx.status,
                gas_price_gwei=tx.gas_price_gwei,
                gas_limit=tx.gas_limit,
                effective_cost_wei=tx.effective_cost_wei,
                created_at=tx.created_at
            )
            for tx in tx_models
        ]

    def update(self, tx: CreatedTransaction) -> CreatedTransaction:
        """Atualiza uma transação existente no banco de dados.

        Args:
            tx (CreatedTransaction): A entidade CreatedTransaction a ser atualizada.

        Returns:
            CreatedTransaction: A entidade CreatedTransaction atualizada.
        
        Raises:
            ValueError: Se a transação com o ID fornecido não for encontrada.
        """
        tx_model = CreatedTransactionModel.query.filter_by(id=tx.id).first()
        if not tx_model:
            raise ValueError(f"Transação com ID {tx.id} não encontrada para atualização.")
        
        tx_model.tx_hash = tx.tx_hash
        tx_model.status = tx.status
        tx_model.gas_price_gwei = tx.gas_price_gwei
        tx_model.gas_limit = tx.gas_limit
        tx_model.effective_cost_wei = tx.effective_cost_wei
        db.session.commit()
        return tx


