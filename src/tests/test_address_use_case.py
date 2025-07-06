
import unittest
from unittest.mock import Mock
from src.application.use_cases.generate_addresses import GenerateAddressesUseCase
from src.domain.entities import Address

class TestGenerateAddressesUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_address_repository = Mock()
        self.mock_blockchain_service = Mock()
        self.use_case = GenerateAddressesUseCase(
            self.mock_address_repository,
            self.mock_blockchain_service
        )

    def test_execute_generates_and_saves_single_address(self):
        # Mock do serviço de blockchain para retornar um novo endereço
        mock_address = Address(address="0x123", private_key="priv_key_1")
        self.mock_blockchain_service.generate_new_address.return_value = mock_address

        # Mock do repositório para retornar o endereço salvo com ID
        self.mock_address_repository.save.return_value = Address(id=1, address="0x123", private_key="priv_key_1")

        # Executa o caso de uso
        result = self.use_case.execute(num_addresses=1)

        # Verifica se os métodos foram chamados corretamente
        self.mock_blockchain_service.generate_new_address.assert_called_once()
        self.mock_address_repository.save.assert_called_once_with(mock_address)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].address, "0x123")
        self.assertIsNotNone(result[0].id)

    def test_execute_generates_and_saves_multiple_addresses(self):
        # Mock para gerar múltiplos endereços
        self.mock_blockchain_service.generate_new_address.side_effect = [
            Address(address=f"0x{i}", private_key=f"priv_key_{i}") for i in range(3)
        ]
        self.mock_address_repository.save.side_effect = [
            Address(id=i+1, address=f"0x{i}", private_key=f"priv_key_{i}") for i in range(3)
        ]

        result = self.use_case.execute(num_addresses=3)

        self.assertEqual(self.mock_blockchain_service.generate_new_address.call_count, 3)
        self.assertEqual(self.mock_address_repository.save.call_count, 3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].address, "0x0")
        self.assertEqual(result[2].address, "0x2")

    def test_execute_with_invalid_num_addresses(self):
        with self.assertRaises(ValueError) as cm:
            self.use_case.execute(num_addresses=0)
        self.assertEqual(str(cm.exception), "Número de endereços inválido.")

        with self.assertRaises(ValueError) as cm:
            self.use_case.execute(num_addresses=-1)
        self.assertEqual(str(cm.exception), "Número de endereços inválido.")

        with self.assertRaises(ValueError) as cm:
            self.use_case.execute(num_addresses="abc")
        self.assertEqual(str(cm.exception), "Número de endereços inválido.")

if __name__ == '__main__':
    unittest.main()


