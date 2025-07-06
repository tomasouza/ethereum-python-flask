
from typing import List, Optional
from src.domain.entities import Address
from src.application.interfaces import IAddressRepository
from src.infrastructure.database.models import db, AddressModel

# Esta camada contém as implementações concretas das interfaces de repositório.
# Ela é responsável por lidar com os detalhes de persistência de dados, como a interação com o banco de dados.
# Aderindo ao Princípio da Inversão de Dependência (D de SOLID), esta classe implementa a interface
# `IAddressRepository` definida na camada de aplicação, sem que a camada de aplicação precise conhecer
# os detalhes de como os dados são armazenados (neste caso, via SQLAlchemy).
# Também adere ao Princípio da Responsabilidade Única (SRP), sendo responsável apenas pela persistência de endereços.

class SQLAlchemyAddressRepository(IAddressRepository):
    """Implementação do repositório de endereços usando SQLAlchemy.

    Esta classe traduz as operações de domínio (definidas em `IAddressRepository`)
    para operações específicas do SQLAlchemy, interagindo com o `AddressModel`.
    """

    def save(self, address: Address) -> Address:
        """Salva um novo endereço no banco de dados.

        Args:
            address (Address): A entidade Address a ser salva.

        Returns:
            Address: A entidade Address salva, com o ID gerado pelo banco de dados.
        """
        new_address_model = AddressModel(
            address=address.address,
            private_key=address.private_key,
            created_at=address.created_at
        )
        db.session.add(new_address_model)
        db.session.commit()
        address.id = new_address_model.id # Atualiza o ID da entidade de domínio
        return address

    def find_by_address(self, address: str) -> Optional[Address]:
        """Busca um endereço pelo seu valor hash.

        Args:
            address (str): O endereço Ethereum a ser buscado.

        Returns:
            Optional[Address]: A entidade Address encontrada, ou None se não existir.
        """
        address_model = AddressModel.query.filter_by(address=address).first()
        if address_model:
            return Address(
                id=address_model.id,
                address=address_model.address,
                private_key=address_model.private_key,
                created_at=address_model.created_at
            )
        return None

    def get_all(self) -> List[Address]:
        """Retorna todos os endereços armazenados.

        Returns:
            List[Address]: Uma lista de todas as entidades Address no banco de dados.
        """
        address_models = AddressModel.query.all()
        return [
            Address(
                id=addr.id,
                address=addr.address,
                private_key=addr.private_key,
                created_at=addr.created_at
            )
            for addr in address_models
        ]


