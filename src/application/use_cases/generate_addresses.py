
from typing import List
from src.domain.entities import Address
from src.application.interfaces import IAddressRepository, IBlockchainService

# Esta camada contém os casos de uso (Use Cases), que representam a lógica de negócio específica da aplicação.
# Eles orquestram o fluxo de dados entre as entidades de domínio e as interfaces (portas) para serviços externos.
# Os casos de uso são independentes de frameworks e bancos de dados, dependendo apenas das interfaces.
# Isso adere ao Princípio da Responsabilidade Única (SRP) e ao Princípio Aberto/Fechado (OCP).

class GenerateAddressesUseCase:
    """Caso de uso para gerar novos endereços Ethereum e persistí-los.

    Este caso de uso coordena a geração de um novo endereço pela camada de infraestrutura
    (via `IBlockchainService`) e sua subsequente persistência pela camada de infraestrutura
    (via `IAddressRepository`). Ele não sabe como o endereço é gerado ou como é salvo,
    apenas que essas operações são possíveis através das interfaces.
    """

    def __init__(self, address_repository: IAddressRepository, blockchain_service: IBlockchainService):
        """
        Inicializa o caso de uso com as dependências necessárias.

        Args:
            address_repository (IAddressRepository): Repositório para persistir endereços.
            blockchain_service (IBlockchainService): Serviço para interagir com a blockchain.
        """
        self.address_repository = address_repository
        self.blockchain_service = blockchain_service

    def execute(self, num_addresses: int = 1) -> List[Address]:
        """
        Executa a geração de endereços.

        Args:
            num_addresses (int): Quantidade de endereços a serem gerados. Padrão é 1.

        Returns:
            List[Address]: Uma lista dos endereços gerados e salvos.
        
        Raises:
            ValueError: Se o número de endereços for inválido.
        """
        if not isinstance(num_addresses, int) or num_addresses <= 0:
            raise ValueError("Número de endereços inválido.")

        generated_addresses = []
        for _ in range(num_addresses):
            # A lógica de geração de endereço é delegada ao serviço de blockchain (SRP).
            # O caso de uso não se importa com os detalhes de como o endereço é gerado.
            new_address_entity = self.blockchain_service.generate_new_address()
            
            # O repositório é responsável pela persistência (SRP).
            # O caso de uso não se importa com os detalhes de como o endereço é salvo.
            saved_address = self.address_repository.save(new_address_entity)
            generated_addresses.append(saved_address)
            
        return generated_addresses


