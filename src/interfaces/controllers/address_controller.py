
from flask import Blueprint, request, jsonify
from src.application.use_cases.generate_addresses import GenerateAddressesUseCase
from src.application.interfaces import IAddressRepository

# Esta camada contém os controladores da API, que são a parte mais externa da Clean Architecture.
# Eles são responsáveis por receber as requisições HTTP, converter os dados de entrada para o formato
# esperado pelos casos de uso, chamar os casos de uso apropriados e formatar a resposta HTTP.
# Os controladores não contêm lógica de negócio e dependem apenas dos casos de uso e das entidades de domínio.
# Isso adere ao Princípio da Responsabilidade Única (SRP) e ao Princípio da Inversão de Dependência (D de SOLID).

# Cria um Blueprint para os endpoints de endereço
address_bp = Blueprint("address", __name__)

def initialize_address_controller(generate_addresses_use_case: GenerateAddressesUseCase, address_repository: IAddressRepository):
    """Inicializa o controlador de endereços com as dependências necessárias.

    Esta função recebe as instâncias dos casos de uso e repositórios necessários
    através de injeção de dependência, garantindo que o controlador não crie suas
    próprias dependências, o que violaria o Princípio da Inversão de Dependência.
    """

    @address_bp.route("/addresses", methods=["POST"])
    def generate_addresses():
        """Endpoint para gerar um ou mais novos endereços Ethereum.

        Recebe o número de endereços a serem gerados, chama o caso de uso
        `GenerateAddressesUseCase` para executar a lógica de negócio e retorna
        a resposta formatada em JSON.
        """
        data = request.get_json()
        num_addresses = data.get("num_addresses", 1)

        try:
            generated_addresses = generate_addresses_use_case.execute(num_addresses)
            return jsonify(
                {
                    "status": "success",
                    "message": f"{len(generated_addresses)} endereços gerados e salvos.",
                    "addresses": [addr.address for addr in generated_addresses]
                }
            ), 201
        except ValueError as e:
            # Captura erros de validação do caso de uso e retorna uma resposta de erro adequada.
            return jsonify({"status": "error", "message": str(e)}), 400
        except Exception as e:
            # Captura quaisquer outras exceções inesperadas e retorna um erro genérico.
            return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

    @address_bp.route("/addresses", methods=["GET"])
    def list_addresses():
        """Endpoint para consultar a lista de todos os endereços gerados e armazenados.

        Recupera todos os endereços através do repositório e retorna a lista formatada em JSON.
        """
        try:
            addresses = address_repository.get_all()
            address_list = [
                {"id": addr.id, "address": addr.address, "created_at": addr.created_at}
                for addr in addresses
            ]
            return jsonify(address_list), 200
        except Exception as e:
            # Captura quaisquer exceções inesperadas e retorna um erro genérico.
            return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

    return address_bp




