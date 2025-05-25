import hashlib
import json
from time import time
from flask import Flask, jsonify, request

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Создание генезис-блока
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Сброс текущих транзакций
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # Убедитесь, что словарь отсортирован, иначе хеши будут непредсказуемыми
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# Создание экземпляра узла
app = Flask(__name__)

# Создание экземпляра блокчейна
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # Запуск алгоритма доказательства работы
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Получение вознаграждения за нахождение доказательства
    blockchain.new_transaction(
        sender="0",
        recipient="your_address",
        amount=1,
    )

    # Создание нового блока
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "Новый блок создан",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Проверка наличия необходимых полей
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Отсутствуют значения', 400

    # Создание новой транзакции
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Транзакция будет добавлена в блок {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
