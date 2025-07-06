
from flask import Blueprint, request, jsonify
from src.application.use_cases.validate_transaction import ValidateTransactionUseCase
from src.application.interfaces import IValidatedTransactionRepository

# Esta camada contém os controladores da API, que são a parte mais externa da Clean Architecture.
# Eles são responsáveis por receber as requisições HTTP, converter os dados de entrada para o formato
# esperado pelos casos de uso, chamar os casos de uso apropriados e formatar a resposta HTTP.
# Os controladores não contêm lógica de negócio e dependem apenas dos casos de uso e das entidades de domínio.
# Isso adere ao Princípio da Responsabilidade Única (SRP) e ao Princípio da Inversão de Dependência (D de SOLID).

# Cria um Blueprint para os endpoints de validação de transação
transaction_validation_bp = Blueprint("transaction_validation", __name__)

def initialize_transaction_validation_controller(validate_transaction_use_case: ValidateTransactionUseCase, validated_tx_repository: IValidatedTransactionRepository):
    """Inicializa o controlador de validação de transações com as dependências necessárias.

    Esta função recebe as instâncias dos casos de uso e repositórios necessários
    através de injeção de dependência, garantindo que o controlador não crie suas
    próprias dependências, o que violaria o Princípio da Inversão de Dependência.
    """

    @transaction_validation_bp.route("/transactions/validations", methods=["POST"])
    def validate_transaction():
        """Endpoint que recebe uma hash de transação e valida sua segurança para gerar crédito.

        Recebe o hash da transação, chama o caso de uso `ValidateTransactionUseCase`
        para executar a lógica de validação e retorna a resposta formatada em JSON.
        """
        data = request.get_json()
        tx_hash = data.get("tx_hash")

        try:
            validation_result = validate_transaction_use_case.execute(tx_hash)
            return jsonify(validation_result), 200
        except ValueError as e:
            # Captura erros de validação do caso de uso e retorna uma resposta de erro adequada.
            return jsonify({"status": "error", "message": str(e)}), 400
        except Exception as e:
            # Captura quaisquer outras exceções inesperadas e retorna um erro genérico.
            return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

    @transaction_validation_bp.route("/transactions/validations", methods=["GET"])
    def validated_transactions_history():
        """Endpoint para consultar o histórico de transações que foram validadas como seguras.

        Recupera o histórico de transações validadas através do repositório e retorna a lista formatada em JSON.
        """
        try:
            history = validated_tx_repository.get_all()
            history_list = [
                {
                    "id": tx.id,
                    "tx_hash": tx.tx_hash,
                    "asset": tx.asset,
                    "to_address": tx.to_address,
                    "value": tx.value,
                    "is_valid": tx.is_valid,
                    "created_at": tx.created_at,
                }
                for tx in history
            ]
            return jsonify(history_list), 200
        except Exception as e:
            # Captura quaisquer exceções inesperadas e retorna um erro genérico.
            return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

    return transaction_validation_bp




