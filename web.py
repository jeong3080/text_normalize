import os
import tensorflow as tf
import numpy as np
from text_normalize_v5 import normalize
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

@app.route("/", methods=['GET'])
def main():
  return render_template('index.html')

@app.route("/", methods=['POST'])
def transliterate():
  input = request.form['input']
  output = normalize(input)
  return jsonify({'input': input, 'output': output})

if __name__ == "__main__":
#  app.debug = True
  app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 30002)))
