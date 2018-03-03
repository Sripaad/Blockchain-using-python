
import json, hashlib
from time import time
from flask import Flask, jsonify, request
from urlparse import urlparse
import requests

def hash(data):
    return hashlib.sha256(data).hexdigest()

def json_to_string(data):
    return json.dumps(data, sort_keys=True).encode()


class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.difficulty = 4
        self.new_block(nounce=0, previous_hash=177888)
        self.nodes = set()

    def get_last_block(self):
        return self.chain[-1]

    def new_transaction(self, sender, receiver, amount):
        transaction = {
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        }
        self.current_transactions.append(transaction)
        return self.get_last_block()['index'] + 1

    def new_block(self, nounce, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'nounce': nounce,
            'previous_hash': previous_hash or hash(json_to_string(self.chain[-1]))
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def proof_of_work(self, previous_data):
        nounce = 0
        while hash(str(previous_data)+str(nounce))[:self.difficulty] != '0000':
            nounce += 1
        return nounce


app = Flask(__name__)

node_name = "qwerty"

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    previous_block = blockchain.get_last_block()
    nounce = blockchain.proof_of_work(previous_block['nounce'])
    blockchain.new_transaction(sender='__0__', receiver=node_name, amount=1)
    previous_hash = hash(json_to_string(previous_block))
    block = blockchain.new_block(nounce, previous_hash)
    response = {
        'message': 'Mining Completed',
        'block': block
    }
    return jsonify(response)

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    index = blockchain.new_transaction(values.get('sender'), values.get('receiver'), values.get('amount'))
    response = { 'message': 'Transaction will be added to block ' + str(index) }
    return jsonify(response)

@app.route('/chain', methods=['GET'])
def chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

