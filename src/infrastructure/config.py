
import os
from web3 import Web3
from src.infrastructure.database.models import db

# Esta camada contém as configurações da aplicação, como URLs de provedores de blockchain
# e strings de conexão com o banco de dados. Ela faz parte da camada de Infraestrutura
# na Clean Architecture, sendo responsável por detalhes de implementação externos.
# A classe `Config` centraliza o acesso a essas configurações, facilitando a manutenção
# e a adaptação a diferentes ambientes (desenvolvimento, produção).

class Config:
    """Classe de configuração para a aplicação.

    Esta classe gerencia as configurações globais da aplicação, como a URI do banco de dados
    e a URL do provedor Web3. Ela atua como um ponto centralizado para acesso a essas
    configurações, garantindo que as camadas internas da aplicação (Domínio e Aplicação)
    não precisem se preocupar com esses detalhes de infraestrutura. Isso contribui para
    o Princípio da Inversão de Dependência (D de SOLID), pois as configurações são
    fornecidas para as camadas que as utilizam, em vez de serem diretamente acopladas.
    """
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///blockchain_data.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WEB3_PROVIDER_URL = os.getenv(
        "WEB3_PROVIDER_URL", "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID"
    )

    @staticmethod
    def init_db(app):
        """Inicializa o SQLAlchemy com a aplicação Flask.

        Esta função é responsável por configurar o banco de dados SQLAlchemy com a aplicação Flask.
        Ela garante que as tabelas do banco de dados sejam criadas se ainda não existirem.
        """
        db.init_app(app)
        with app.app_context():
            db.create_all()

    @staticmethod
    def get_web3_instance() -> Web3:
        """Retorna uma instância configurada do Web3.

        Esta função fornece uma instância do Web3.py configurada com a URL do provedor.
        Ela abstrai a criação da instância do Web3 das outras partes da aplicação,
        promovendo a Inversão de Dependência.
        """
        return Web3(Web3.HTTPProvider(Config.WEB3_PROVIDER_URL))




