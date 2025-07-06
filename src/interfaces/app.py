
from flask import Flask
import os

from src.infrastructure.config import Config
from src.infrastructure.database.models import db
from src.infrastructure.repositories.sqlalchemy_address_repository import SQLAlchemyAddressRepository
from src.infrastructure.repositories.sqlalchemy_validated_transaction_repository import SQLAlchemyValidatedTransactionRepository
from src.infrastructure.repositories.sqlalchemy_created_transaction_repository import SQLAlchemyCreatedTransactionRepository
from src.infrastructure.services.web3_blockchain_service import Web3BlockchainService

from src.application.use_cases.generate_addresses import GenerateAddressesUseCase
from src.application.use_cases.validate_transaction import ValidateTransactionUseCase
from src.application.use_cases.create_transaction import CreateTransactionUseCase, UpdateTransactionStatusUseCase

from src.interfaces.controllers.address_controller import initialize_address_controller
from src.interfaces.controllers.transaction_validation_controller import initialize_transaction_validation_controller
from src.interfaces.controllers.transaction_creation_controller import initialize_transaction_creation_controller

# Esta é a camada de Interfaces (a mais externa na Clean Architecture).
# O arquivo `app.py` atua como o ponto de entrada da aplicação Flask e é responsável
# pela composição de todas as dependências e pela inicialização dos controladores.
# Ele demonstra o Princípio da Inversão de Dependência (D de SOLID) ao injetar
# as implementações concretas das dependências nos casos de uso e controladores.

def create_app():
    """Cria e configura a aplicação Flask, injetando as dependências."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa o banco de dados
    # A configuração do DB é delegada à classe Config, mantendo a responsabilidade única.
    Config.init_db(app)

    # Inicializa o serviço de blockchain
    # A instância do serviço de blockchain é criada aqui e injetada nos casos de uso.
    # Isso garante que os casos de uso não dependam diretamente da implementação do Web3.py,
    # mas sim da interface IBlockchainService, aderindo ao DIP.
    web3_service = Web3BlockchainService(Config.WEB3_PROVIDER_URL)

    # Inicializa os repositórios
    # As implementações concretas dos repositórios são criadas aqui.
    # Elas implementam as interfaces definidas na camada de aplicação, permitindo a substituição
    # por outras implementações (ex: MongoDB, PostgreSQL) sem afetar as camadas internas (LSP).
    address_repository = SQLAlchemyAddressRepository()
    validated_tx_repository = SQLAlchemyValidatedTransactionRepository()
    created_tx_repository = SQLAlchemyCreatedTransactionRepository()

    # Inicializa os casos de uso
    # Os casos de uso recebem suas dependências (repositórios e serviços) via injeção.
    # Isso reforça o DIP e o SRP, pois os casos de uso se concentram apenas na lógica de negócio,
    # sem se preocupar com a criação ou gerenciamento de suas dependências.
    generate_addresses_use_case = GenerateAddressesUseCase(address_repository, web3_service)
    validate_transaction_use_case = ValidateTransactionUseCase(validated_tx_repository, address_repository, web3_service)
    create_transaction_use_case = CreateTransactionUseCase(created_tx_repository, address_repository, web3_service)
    update_transaction_status_use_case = UpdateTransactionStatusUseCase(created_tx_repository, web3_service)

    # Inicializa e registra os Blueprints dos controladores
    # Os controladores são inicializados com os casos de uso e repositórios necessários.
    # Eles atuam como adaptadores entre as requisições HTTP e a lógica de negócio (casos de uso).
    # Isso mantém os controladores independentes da lógica de negócio, aderindo ao SRP.
    app.register_blueprint(initialize_address_controller(generate_addresses_use_case, address_repository))
    app.register_blueprint(initialize_transaction_validation_controller(validate_transaction_use_case, validated_tx_repository))
    app.register_blueprint(initialize_transaction_creation_controller(create_transaction_use_case, update_transaction_status_use_case, created_tx_repository))

    return app

if __name__ == '__main__':
    # Ponto de entrada da aplicação Flask.
    # `debug=True` é útil para desenvolvimento, mas deve ser `False` em produção.
    # `host='0.0.0.0'` permite que a aplicação seja acessível externamente (necessário no ambiente sandbox).
    # `port=5000` define a porta em que a API estará escutando.
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)


