
from flask import Blueprint, request, jsonify
from src.application.use_cases.create_transaction import CreateTransactionUseCase, UpdateTransactionStatusUseCase
from src.application.interfaces import ICreatedTransactionRepository

# Esta camada contém os controladores da API, que são a parte mais externa da Clean Architecture.
# Eles são responsáveis por receber as requisições HTTP, converter os dados de entrada para o formato
# esperado pelos casos de uso, chamar os casos de uso apropriados e formatar a resposta HTTP.
# Os controladores não contêm lógica de negócio e dependem apenas dos casos de uso e das entidades de domínio.
# Isso adere ao Princípio da Responsabilidade Única (SRP) e ao Princípio da Inversão de Dependência (D de SOLID).

# Cria um Blueprint para os endpoints de criação de transação
transaction_creation_bp = Blueprint("transaction_creation", __name__)

def initialize_transaction_creation_controller(create_transaction_use_case: CreateTransactionUseCase, update_transaction_status_use_case: UpdateTransactionStatusUseCase, created_tx_repository: ICreatedTransactionRepository):
    """Inicializa o controlador de criação de transações com as dependências necessárias.

    Esta função recebe as instâncias dos casos de uso e repositórios necessários
    através de injeção de dependência, garantindo que o controlador não crie suas
    próprias dependências, o que violaria o Princípio da Inversão de Dependência.
    """

    @transaction_creation_bp.route("/transactions", methods=["POST"])
    def create_transaction():
        """Endpoint para gerar e enviar uma transação on-chain (ETH ou ERC-20).

        Recebe os detalhes da transação, chama o caso de uso `CreateTransactionUseCase`
        para executar a lógica de negócio e retorna a resposta formatada em JSON.
        """
        data = request.get_json()
        from_address = data.get("from_address")
        to_address = data.get("to_address")
        asset = data.get("asset")
        value = data.get("value")

        try:
            new_tx = create_transaction_use_case.execute(from_address, to_address, asset, value)
            return jsonify(
                {
                    "status": "success",
                    "message": "Transação enviada com sucesso.",
                    "tx_hash": new_tx.tx_hash
                }
            ), 200
        except ValueError as e:
            # Captura erros de validação do caso de uso e retorna uma resposta de erro adequada.
            return jsonify({"status": "error", "message": str(e)}), 400
        except Exception as e:
            # Captura quaisquer outras exceções inesperadas e retorna um erro genérico.
            return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

    @transaction_creation_bp.route("/transactions", methods=["GET"])
    def created_transactions_history():
        """Endpoint para consultar o histórico de transações que foram criadas pela aplicação.

        Recupera o histórico de transações criadas através do repositório e retorna a lista formatada em JSON.
        """
        try:
            history = created_tx_repository.get_all()
            history_list = [
                {
                    "id": tx.id,
                    "tx_hash": tx.tx_hash,
                    "from_address": tx.from_address,
                    "to_address": tx.to_address,
                    "asset": tx.asset,
                    "value": tx.value,
                    "status": tx.status,
                    "gas_price_gwei": tx.gas_price_gwei,
                    "gas_limit": tx.gas_limit,
                    "effective_cost_wei": tx.effective_cost_wei,
                    "created_at": tx.created_at,
                }
                for tx in history
            ]
            return jsonify(history_list), 200
        except Exception as e:
            # Captura quaisquer outras exceções inesperadas e retorna um erro genérico.
            return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

    @transaction_creation_bp.route("/transactions/<tx_hash>", methods=["PATCH"])
    def update_transaction_status(tx_hash):
        """Endpoint para atualizar o status de uma transação criada após sua confirmação na rede.

        Recebe o hash da transação, chama o caso de uso `UpdateTransactionStatusUseCase`
        para executar a lógica de atualização e retorna a resposta formatada em JSON.
        """

        try:
            updated_tx = update_transaction_status_use_case.execute(tx_hash)
            return jsonify(
                {
                    "status": "success",
                    "message": f"Status da transação {tx_hash} atualizado para {updated_tx.status}.",
                }
            ), 200
        except ValueError as e:
            # Captura erros de validação do caso de uso e retorna uma resposta de erro adequada.
            return jsonify({"status": "error", "message": str(e)}), 400
        except Exception as e:
            # Captura quaisquer outras exceções inesperadas e retorna um erro genérico.
            return jsonify({"status": "error", "message": f"Erro interno: {str(e)}"}), 500

    return transaction_creation_bp




