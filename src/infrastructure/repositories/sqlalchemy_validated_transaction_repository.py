
from typing import List, Optional
from src.domain.entities import ValidatedTransaction
from src.application.interfaces import IValidatedTransactionRepository
from src.infrastructure.database.models import db, ValidatedTransactionModel

# Esta camada contém as implementações concretas das interfaces de repositório.
# Ela é responsável por lidar com os detalhes de persistência de dados, como a interação com o banco de dados.
# Aderindo ao Princípio da Inversão de Dependência (D de SOLID), esta classe implementa a interface
# `IValidatedTransactionRepository` definida na camada de aplicação, sem que a camada de aplicação precise conhecer
# os detalhes de como os dados são armazenados (neste caso, via SQLAlchemy).
# Também adere ao Princípio da Responsabilidade Única (SRP), sendo responsável apenas pela persistência de transações validadas.

class SQLAlchemyValidatedTransactionRepository(IValidatedTransactionRepository):
    """Implementação do repositório de transações validadas usando SQLAlchemy.

    Esta classe traduz as operações de domínio (definidas em `IValidatedTransactionRepository`)
    para operações específicas do SQLAlchemy, interagindo com o `ValidatedTransactionModel`.
    """

    def save(self, tx: ValidatedTransaction) -> ValidatedTransaction:
        """Salva uma nova transação validada no banco de dados.

        Args:
            tx (ValidatedTransaction): A entidade ValidatedTransaction a ser salva.

        Returns:
            ValidatedTransaction: A entidade ValidatedTransaction salva, com o ID gerado pelo banco de dados.
        """
        new_tx_model = ValidatedTransactionModel(
            tx_hash=tx.tx_hash,
            asset=tx.asset,
            to_address=tx.to_address,
            value=tx.value,
            is_valid=tx.is_valid,
            created_at=tx.created_at
        )
        db.session.add(new_tx_model)
        db.session.commit()
        tx.id = new_tx_model.id
        return tx

    def find_by_hash(self, tx_hash: str) -> Optional[ValidatedTransaction]:
        """Busca uma transação validada pelo seu hash.

        Args:
            tx_hash (str): O hash da transação a ser buscada.

        Returns:
            Optional[ValidatedTransaction]: A entidade ValidatedTransaction encontrada, ou None se não existir.
        """
        tx_model = ValidatedTransactionModel.query.filter_by(tx_hash=tx_hash).first()
        if tx_model:
            return ValidatedTransaction(
                id=tx_model.id,
                tx_hash=tx_model.tx_hash,
                asset=tx_model.asset,
                to_address=tx_model.to_address,
                value=tx_model.value,
                is_valid=tx_model.is_valid,
                created_at=tx_model.created_at
            )
        return None

    def get_all(self) -> List[ValidatedTransaction]:
        """Retorna todas as transações validadas armazenadas.

        Returns:
            List[ValidatedTransaction]: Uma lista de todas as entidades ValidatedTransaction no banco de dados.
        """
        tx_models = ValidatedTransactionModel.query.all()
        return [
            ValidatedTransaction(
                id=tx.id,
                tx_hash=tx.tx_hash,
                asset=tx.asset,
                to_address=tx.to_address,
                value=tx.value,
                is_valid=tx.is_valid,
                created_at=tx.created_at
            )
            for tx in tx_models
        ]


