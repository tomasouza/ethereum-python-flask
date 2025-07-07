# ethereum-python-flask

A solução implementa uma API RESTful para interagir com a blockchain Ethereum, focando na geração de endereços, validação de transações e criação de transações.

## Arquitetura do Projeto: Clean Architecture

A arquitetura do projeto segue os princípios da Clean Architecture, proposta por Robert C. Martin (Uncle Bob). Esta abordagem organiza o código em camadas concêntricas, onde as dependências fluem apenas de fora para dentro. Isso garante que as regras de negócio mais importantes (o Core da aplicação) sejam independentes de frameworks, bancos de dados e interfaces de usuário.

### Camadas:

1.  **Domain (Domínio - `src/domain`)**: Esta é a camada mais interna e contém as regras de negócio da aplicação. É completamente independente de qualquer tecnologia externa (frameworks, bancos de dados, etc.).
    *   **Entities (`entities.py`)**: Contém as classes que representam os objetos de negócio e suas regras. Ex: `Address`, `ValidatedTransaction`, `CreatedTransaction`, `TransferDetail`.

2.  **Application (Aplicação - `src/application`)**: Esta camada contém os casos de uso (use cases) da aplicação, que orquestram o fluxo de dados de e para as entidades do domínio. Ela define as interfaces (portas) que serão implementadas pelas camadas externas.
    *   **Interfaces (`interfaces.py`)**: Define os contratos (ABCs) para os repositórios e serviços externos que a camada de aplicação precisa. Isso garante a Inversão de Dependência (D de SOLID).
    *   **Use Cases (`use_cases/`)**: Contém a lógica de negócio específica da aplicação, que coordena as entidades e interage com as interfaces definidas. Ex: `GenerateAddressesUseCase`, `ValidateTransactionUseCase`, `CreateTransactionUseCase`, `UpdateTransactionStatusUseCase`.

3.  **Infrastructure (Infraestrutura - `src/infrastructure`)**: Esta camada é responsável por implementar as interfaces definidas na camada de aplicação. Ela lida com os detalhes de implementação, como acesso a banco de dados, comunicação com serviços externos (blockchain) e configuração.
    *   **Database (`database/`)**: Contém os modelos ORM (SQLAlchemy) e a configuração do banco de dados.
    *   **Repositories (`repositories/`)**: Implementações concretas das interfaces de repositório, usando SQLAlchemy para persistência. Ex: `SQLAlchemyAddressRepository`.
    *   **Services (`services/`)**: Implementações concretas das interfaces de serviço externo, como a interação com a blockchain via Web3.py. Ex: `Web3BlockchainService`.
    *   **Config (`config.py`)**: Gerencia as configurações da aplicação, como URLs de provedores e strings de conexão com o banco de dados.

4.  **Interfaces (Interfaces - `src/interfaces`)**: Esta é a camada mais externa e contém as interfaces de usuário ou APIs. Ela adapta os dados para o formato necessário para a camada de aplicação e apresenta os resultados.
    *   **Controllers (`controllers/`)**: Contém os controladores da API Flask, que recebem as requisições HTTP, chamam os casos de uso apropriados e retornam as respostas. Ex: `address_controller.py`.
    *   **App (`app.py`)**: O ponto de entrada da aplicação Flask, responsável pela inicialização e injeção de dependências.

## Princípios SOLID Aplicados

Os princípios SOLID foram aplicados em toda a refatoração para garantir um código mais robusto e manutenível:

*   **S - Single Responsibility Principle (Princípio da Responsabilidade Única)**:
    *   Cada classe e módulo tem uma única responsabilidade bem definida. Por exemplo, `Address` (entidade) apenas representa um endereço, `GenerateAddressesUseCase` (caso de uso) apenas orquestra a geração de endereços, e `SQLAlchemyAddressRepository` (repositório) apenas lida com a persistência de endereços.
    *   Os controladores Flask são responsáveis apenas por receber requisições HTTP, chamar o caso de uso apropriado e retornar a resposta, sem lógica de negócio.

*   **O - Open/Closed Principle (Princípio Aberto/Fechado)**:
    *   As entidades de domínio e os casos de uso são abertos para extensão, mas fechados para modificação. Novas formas de persistência ou novos serviços de blockchain podem ser adicionados implementando as interfaces (`IAddressRepository`, `IBlockchainService`) sem alterar o código dos casos de uso.

*   **L - Liskov Substitution Principle (Princípio da Substituição de Liskov)**:
    *   As implementações concretas dos repositórios e serviços (ex: `SQLAlchemyAddressRepository`, `Web3BlockchainService`) podem ser substituídas por outras implementações (ex: um repositório MongoDB ou um serviço de blockchain diferente) sem quebrar a funcionalidade da camada de aplicação, pois todas aderem às mesmas interfaces.

*   **I - Interface Segregation Principle (Princípio da Segregação de Interfaces)**:
    *   As interfaces (`IAddressRepository`, `IBlockchainService`, etc.) são específicas para cada cliente (caso de uso ou repositório). Em vez de uma única interface grande, temos interfaces menores e mais coesas, garantindo que as classes não sejam forçadas a implementar métodos que não utilizam.

*   **D - Dependency Inversion Principle (Princípio da Inversão de Dependência)**:
    *   As camadas de alto nível (casos de uso) não dependem de detalhes de implementação das camadas de baixo nível (repositórios, serviços de blockchain). Ambas dependem de abstrações (interfaces). A injeção de dependências (`app.py`) é usada para fornecer as implementações concretas para os casos de uso, invertendo o fluxo tradicional de dependência.

## Como Rodar o Projeto

### Pré-requisitos

*   Python 3.8+
*   pip
*   Uma URL de provedor Ethereum (Infura, Alchemy, etc.) para a rede Sepolia. Você pode obter uma gratuitamente em [Infura](https://www.infura.io/) ou [Alchemy](https://www.alchemy.com/).

### Configuração

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd ethereum-python-flask
    ```

2.  **Crie e ative um ambiente virtual:**

    No Windows:
    ```
    python -m venv venv
    venv\Scripts\activate
    ```

    No Linux/Mac:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```
    pip install -r requirements.txt
    ```

4.  **Configure a URL do provedor Ethereum:**

    Abra o arquivo `src\infrastructure\config.py` e substitua `https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID` pela sua URL de provedor Infura/Alchemy para a rede Sepolia.

    Alternativamente, você pode configurar uma variável de ambiente com o nome WEB3_PROVIDER_URL:

    No Windows (PowerShell):
    ```
    $env:WEB3_PROVIDER_URL = "https://sepolia.infura.io/v3/SEU_ID_DO_PROJETO_INFURA"
    ```

    No Windows (CMD):
    ```
    set WEB3_PROVIDER_URL=https://sepolia.infura.io/v3/SEU_ID_DO_PROJETO_INFURA
    ```

    No Linux/Mac:
    ```bash
    export WEB3_PROVIDER_URL="https://sepolia.infura.io/v3/SEU_ID_DO_PROJETO_INFURA"
    ```

### Executando a Aplicação

Para iniciar a API Flask:

No Windows:
```
set PYTHONPATH=.
python -m src.interfaces.app
```

No Linux/Mac:
```bash
PYTHONPATH=. python3 -m src.interfaces.app
```

A aplicação será iniciada em `http://127.0.0.1:5000` e estará acessível no seu navegador ou via ferramentas como Postman.

### Testando a API

Você pode testar a API usando o Postman ou curl. Uma coleção do Postman está disponível no arquivo `postman-collection.json` na raiz do projeto.

Para importar a coleção no Postman:
1. Abra o Postman
2. Clique em "Import" no canto superior esquerdo
3. Selecione o arquivo `postman-collection.json`
4. Agora você pode executar as requisições pré-configuradas para testar a API
5. Você precisará de ETH para isto crie uma carteira em seguida utilize um faucet para receber fundos: `https://cloud.google.com/application/web3/faucet/ethereum/sepolia`

### Endpoints da API

Todos os endpoints retornam JSON.

#### Geração de Endereços

*   **`POST /addresses`**
    *   **Descrição**: Gera um ou mais novos endereços Ethereum e suas chaves privadas, armazenando-os no banco de dados.
    *   **Corpo da Requisição (JSON)**:
        ```json
        {
            "num_addresses": 1  // Opcional, padrão é 1
        }
        ```
    *   **Exemplo de Resposta (Sucesso)**:
        ```json
        {
            "status": "success",
            "message": "1 endereços gerados e salvos.",
            "addresses": [
                "0xAbCdEfGhIjKlMnOpQrStUvWxYz0123456789AbC"
            ]
        }
        ```

*   **`GET /addresses`**
    *   **Descrição**: Retorna a lista de todos os endereços Ethereum gerados e armazenados.
    *   **Exemplo de Resposta (Sucesso)**:
        ```json
        [
            {
                "id": 1,
                "address": "0xAbCdEfGhIjKlMnOpQrStUvWxYz0123456789AbC",
                "created_at": "2023-10-27T10:00:00.000Z"
            }
        ]
        ```

#### Transações

*   **`POST /transactions`**
    *   **Descrição**: Cria e envia uma transação de ETH ou token ERC-20 para a rede Ethereum. A chave privada do `from_address` deve estar armazenada na aplicação.
    *   **Corpo da Requisição (JSON)**:
        ```json
        {
            "from_address": "0xOurAddress",
            "to_address": "0xRecipientAddress",
            "asset": "ETH", // ou endereço do contrato ERC-20
            "value": "0.1" // Valor em ETH ou no token
        }
        ```
    *   **Exemplo de Resposta (Sucesso)**:
        ```json
        {
            "status": "success",
            "message": "Transação enviada com sucesso.",
            "tx_hash": "0xdef456..."
        }
        ```

*   **`GET /transactions`**
    *   **Descrição**: Retorna o histórico de transações que foram criadas e enviadas pela aplicação.
    *   **Exemplo de Resposta (Sucesso)**:
        ```json
        [
            {
                "id": 1,
                "tx_hash": "0xdef456...",
                "from_address": "0xOurAddress",
                "to_address": "0xRecipientAddress",
                "asset": "ETH",
                "value": "0.1",
                "status": "pending",
                "gas_price_gwei": "20",
                "gas_limit": 21000,
                "effective_cost_wei": null,
                "created_at": "2023-10-27T10:10:00.000Z"
            }
        ]
        ```
        
*   **`PATCH /transactions/<tx_hash>`**
    *   **Descrição**: Atualiza o status de uma transação criada pela aplicação, verificando seu status na blockchain (confirmada, falha).
    *   **Parâmetro de URL**: `tx_hash` (hash da transação)
    *   **Exemplo de Resposta (Sucesso)**:
        ```json
        {
            "status": "success",
            "message": "Status da transação 0xdef456... atualizado para confirmed."
        }
        ```

#### Validação de Transações

*   **`POST /transactions/validations`**
    *   **Descrição**: Valida uma transação Ethereum (ETH ou ERC-20) pelo seu hash, verificando sua segurança para fins de crédito (confirmações, status, destino).
    *   **Corpo da Requisição (JSON)**:
        ```json
        {
            "tx_hash": "0x123abc..." // Hash da transação
        }
        ```
    *   **Exemplo de Resposta (Sucesso)**:
        ```json
        {
            "tx_hash": "0x123abc...",
            "is_valid_and_safe_for_credit": true,
            "transfers": [
                {
                    "asset": "ETH",
                    "to_address": "0xOurAddress",
                    "value": "1.5"
                }
            ],
            "confirmations": 25,
            "tx_status": "success"
        }
        ```

*   **`GET /transactions/validations`**
    *   **Descrição**: Retorna o histórico de transações que foram validadas como seguras para crédito.
    *   **Exemplo de Resposta (Sucesso)**:
        ```json
        [
            {
                "id": 1,
                "tx_hash": "0x123abc...",
                "asset": "ETH",
                "to_address": "0xOurAddress",
                "value": "1.5",
                "is_valid": true,
                "created_at": "2023-10-27T10:05:00.000Z"
            }
        ]
        ```

## Boas Práticas de Segurança

Embora este seja um projeto de demonstração, algumas boas práticas de segurança foram consideradas:

*   **Separação de Responsabilidades**: A Clean Architecture ajuda a isolar as regras de negócio sensíveis (como a manipulação de chaves privadas) em camadas específicas, tornando-as menos suscetíveis a vulnerabilidades em outras partes do sistema.
*   **Armazenamento de Chaves Privadas**: No exemplo, as chaves privadas são armazenadas em texto simples no banco de dados para simplicidade. **Em um ambiente de produção, elas DEVERIAM ser criptografadas usando técnicas robustas (ex: AES256) e/ou gerenciadas por um serviço de gerenciamento de segredos (ex: AWS Secrets Manager, HashiCorp Vault) ou um Hardware Security Module (HSM).**
*   **Validação de Entrada**: Todas as entradas da API são validadas para prevenir ataques comuns como injeção de SQL ou dados malformados.
*   **Tratamento de Erros**: Erros são capturados e retornados de forma genérica para evitar a exposição de detalhes internos da aplicação.
*   **Dependências**: As dependências são gerenciadas via `requirements.txt`, incentivando o uso de versões fixas e a verificação de vulnerabilidades conhecidas.
*   **Confirmações de Transação**: A validação de transações para crédito exige um número mínimo de confirmações na blockchain, mitigando riscos de reorganização da cadeia (reorgs).

## Conhecimentos em Blockchain

Este projeto demonstra conhecimentos em blockchain através dos seguintes pontos:

*   **Interação com Ethereum**: Utilização da biblioteca `web3.py` para se conectar a um nó Ethereum (Infura), enviar transações, obter detalhes de transações e recibos, e interagir com contratos inteligentes (ERC-20).
*   **Geração de Endereços**: Compreensão do processo de geração de pares de chaves pública/privada e endereços Ethereum.
*   **Tipos de Transação**: Distinção entre transações nativas de ETH e transações de token ERC-20, incluindo a decodificação de logs de eventos para identificar transferências de tokens.
*   **Validação de Transações**: Implementação de lógica para verificar a validade e segurança de uma transação, considerando o status da transação, número de confirmações e o endereço de destino.
*   **Criação e Assinatura de Transações**: Conhecimento sobre como construir, assinar e transmitir transações para a rede Ethereum, incluindo o cálculo de `gas price` e `gas limit`.
*   **Gerenciamento de Chaves**: Embora simplificado para demonstração, o projeto aborda o conceito de gerenciamento de chaves privadas para assinar transações.
*   **Padrões de Projeto**: Aplicação de padrões de projeto como Repositório e Serviço para abstrair a interação com a blockchain e o banco de dados, tornando o código mais limpo e testável.

Este projeto serve como uma base sólida para uma aplicação mais complexa, com a flexibilidade de adaptar-se a diferentes provedores de blockchain, bancos de dados e interfaces de usuário, mantendo a robustez e a manutenibilidade do código.
