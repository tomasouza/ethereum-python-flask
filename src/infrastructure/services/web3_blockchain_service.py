
import os
import json
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from typing import Optional, Dict

from src.application.interfaces import IBlockchainService
from src.domain.entities import Address, TransferDetail

# Esta camada contém as implementações concretas das interfaces de serviço.
# Ela é responsável por lidar com os detalhes de interação com a blockchain Ethereum,
# utilizando a biblioteca `web3.py`. Aderindo ao Princípio da Inversão de Dependência (D de SOLID),
# esta classe implementa a interface `IBlockchainService` definida na camada de aplicação,
# sem que a camada de aplicação precise conhecer os detalhes de como a interação com a blockchain ocorre.
# Também adere ao Princípio da Responsabilidade Única (SRP), sendo responsável apenas pelas operações de blockchain.
# O Princípio da Substituição de Liskov (LSP) é respeitado, pois esta implementação pode ser substituída
# por outra que adere à mesma interface, sem quebrar o sistema.

# ABI mínimo para um contrato ERC-20 (apenas a função transfer e o evento Transfer)
# Este ABI é um exemplo de como interagir com contratos inteligentes usando um ABI simplificado,
# demonstrando conhecimento sobre a estrutura de contratos ERC-20.
ERC20_ABI = """
[
    {
        "constant": false,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]
"""

class Web3BlockchainService(IBlockchainService):
    """Implementação do serviço de blockchain usando Web3.py.

    Esta classe é responsável por todas as interações de baixo nível com a rede Ethereum,
    como a conexão com o nó, a geração de chaves, a consulta de transações e o envio de transações.
    Ela atua como um adaptador entre a camada de aplicação e a biblioteca `web3.py`.
    """

    def __init__(self, provider_url: str):
        """
        Inicializa o serviço de blockchain com a URL do provedor.

        Args:
            provider_url (str): A URL do provedor Web3 (ex: Infura, Alchemy).

        Raises:
            ConnectionError: Se não for possível conectar à rede Ethereum.
        """
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Não foi possível conectar à rede Ethereum em {provider_url}")
        print(f"Conectado à rede Ethereum: {self.w3.is_connected()}")
        print(f"Bloco atual: {self.w3.eth.block_number}")

    def generate_new_address(self) -> Address:
        """Gera um novo par de chaves e endereço Ethereum.

        Returns:
            Address: Uma entidade Address contendo o endereço e a chave privada.
        """
        account = Account.create()
        return Address(address=account.address, private_key=account.key.hex())

    def get_transaction_details(self, tx_hash: str) -> Dict:
        """Obtém os detalhes de uma transação pelo seu hash.

        Args:
            tx_hash (str): O hash da transação.

        Returns:
            Dict: Um dicionário contendo os detalhes da transação, ou um dicionário vazio se não encontrada.
        """
        tx = self.w3.eth.get_transaction(tx_hash)
        if tx:
            # Converte o objeto Transaction para um dicionário serializável
            return {
                "blockHash": tx.blockHash.hex() if tx.blockHash else None,
                "blockNumber": tx.blockNumber,
                "from": tx["from"],
                "gas": tx.gas,
                "gasPrice": tx.gasPrice,
                "hash": tx.hash.hex(),
                "input": tx.input,
                "nonce": tx.nonce,
                "to": tx.to,
                "transactionIndex": tx.transactionIndex,
                "value": tx.value,
                "type": tx.type,
                "v": tx.v,
                "r": tx.r.hex(),
                "s": tx.s.hex()
            }
        return {}

    def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """Obtém o recibo de uma transação pelo seu hash.

        Args:
            tx_hash (str): O hash da transação.

        Returns:
            Dict: Um dicionário contendo o recibo da transação, ou um dicionário vazio se não encontrado.
        """
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        if receipt:
            # Converte o objeto TransactionReceipt para um dicionário serializável
            return {
                "blockHash": receipt.blockHash.hex(),
                "blockNumber": receipt.blockNumber,
                "contractAddress": receipt.contractAddress,
                "cumulativeGasUsed": receipt.cumulativeGasUsed,
                "effectiveGasPrice": receipt.effectiveGasPrice,
                "from": receipt["from"],
                "gasUsed": receipt.gasUsed,
                "logs": [
                    {
                        "address": log.address,
                        "blockHash": log.blockHash.hex(),
                        "blockNumber": log.blockNumber,
                        "data": log.data,
                        "logIndex": log.logIndex,
                        "removed": log.removed,
                        "topics": [topic.hex() for topic in log.topics],
                        "transactionHash": log.transactionHash.hex(),
                        "transactionIndex": log.transactionIndex,
                        "id": log.id
                    }
                    for log in receipt.logs
                ],
                "logsBloom": receipt.logsBloom.hex(),
                "status": receipt.status,
                "to": receipt.to,
                "transactionHash": receipt.transactionHash.hex(),
                "transactionIndex": receipt.transactionIndex,
                "type": receipt.type
            }
        return {}

    def get_current_block_number(self) -> int:
        """Retorna o número do bloco atual da rede Ethereum.

        Returns:
            int: O número do bloco atual.
        """
        return self.w3.eth.block_number

    def decode_erc20_transfer_log(self, log: Dict) -> Optional[TransferDetail]:
        """Decodifica um log de evento `Transfer` de um token ERC-20.

        Args:
            log (Dict): O dicionário de log da transação.

        Returns:
            Optional[TransferDetail]: Um objeto TransferDetail se o log for um evento de transferência ERC-20,
                                      caso contrário, None.
        """
        TRANSFER_EVENT_TOPIC = self.w3.keccak(text='Transfer(address,address,uint256)').hex()

        if log.get("topics") and log["topics"][0] == TRANSFER_EVENT_TOPIC:
            try:
                # O `to` address está no topic[2] (indexado)
                to_address_erc20 = self.w3.to_checksum_address("0x" + log["topics"][2][-40:])
                # O valor está nos dados do log (não indexado)
                value_erc20_raw = int(log["data"], 16)

                # Placeholder para o símbolo do token e decimais.
                # Em um cenário real, essas informações seriam obtidas consultando o contrato do token.
                token_symbol = "ERC-20 Token"
                token_decimals = 18  # Assumindo 18 decimais como padrão para muitos tokens

                value_erc20_readable = value_erc20_raw / (10**token_decimals)

                return TransferDetail(
                    asset=token_symbol,
                    to_address=to_address_erc20,
                    value=str(value_erc20_readable)
                )
            except Exception as e:
                print(f"Erro ao decodificar log ERC-20: {e}")
                return None
        return None

    def create_and_sign_transaction(
        self, from_address: str, to_address: str, asset: str, value: str, private_key: str
    ) -> tuple[str, Dict]:
        """Cria e assina uma transação (ETH ou ERC-20).

        Args:
            from_address (str): Endereço de origem da transação.
            to_address (str): Endereço de destino da transação.
            asset (str): O ativo a ser transferido (
                "ETH" ou o endereço do contrato do token ERC-20
            ).
            value (str): O valor a ser transferido em formato decimal.
            private_key (str): A chave privada do endereço de origem.

        Returns:
            tuple[str, Dict]: Uma tupla contendo o hash da transação bruta assinada (hex) e os detalhes da transação.
        """
        # Converte o valor para o formato correto (Wei para ETH, ou com base nos decimais do token)
        if asset == "ETH":
            value_in_wei = self.w3.to_wei(float(value), "ether")
        else:
            token_decimals = 18
            value_in_wei = int(float(value) * (10**token_decimals))

        sender_account: LocalAccount = Account.from_key(private_key)

        gas_price = self.w3.eth.gas_price
        gas_price_with_margin = int(gas_price * 1.20)

        transaction = {
            "from": sender_account.address,
            "nonce": self.w3.eth.get_transaction_count(sender_account.address),
            "gasPrice": gas_price_with_margin,
            "chainId": self.w3.eth.chain_id,
        }

        if asset == "ETH":
            transaction["to"] = to_address
            transaction["value"] = value_in_wei
            gas_limit = self.w3.eth.estimate_gas(transaction)
            transaction["gas"] = gas_limit
        else:
            token_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(asset), abi=json.loads(ERC20_ABI)
            )
            transfer_function = token_contract.functions.transfer(
                self.w3.to_checksum_address(to_address), value_in_wei
            )
            transaction["to"] = self.w3.to_checksum_address(asset)
            transaction["data"] = transfer_function._encode_transaction_data()
            gas_limit = self.w3.eth.estimate_gas(transaction)
            transaction["gas"] = gas_limit
            transaction["value"] = 0

        signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key)
        return signed_transaction.rawTransaction.hex(), transaction # Retorna o raw_tx_hex e os detalhes da transação

    def send_raw_transaction(self, raw_tx: str) -> str:
        """Envia uma transação bruta assinada para a rede Ethereum.

        Args:
            raw_tx (str): A transação bruta assinada em formato hexadecimal.

        Returns:
            str: O hash da transação enviada.
        """
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx).hex()
        return tx_hash


