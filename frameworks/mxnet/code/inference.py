from __future__ import print_function

import logging

from mxnet import gluon
import mxnet as mx

import numpy as np
import json
import os

logging.basicConfig(level=logging.DEBUG)

def model_fn(model_dir):
    """Load the gluon model. Called once when hosting service starts.

    :param: model_dir The directory where model files are stored.
    :return: a model (in this case a Gluon network)
    """
    net = gluon.SymbolBlock.imports(
            symbol_file=os.path.join(model_dir, 'compiled-symbol.json'),
            input_names=['data'],
            param_file=os.path.join(model_dir, 'compiled-0000.params'))
    return net

def transform_fn(net, data, input_content_type, output_content_type):
    assert input_content_type=='application/json'
    assert output_content_type=='application/json' 

    # parsed should be a 1d array of length 728
    parsed = json.loads(data)
    parsed = parsed['inputs'] 
    
    # convert to numpy array
    arr = np.array(parsed).reshape(-1, 1, 28, 28)
    
    # convert to mxnet ndarray
    nda = mx.nd.array(arr)

    output = net(nda)
    
    prediction = mx.nd.argmax(output, axis=1)
    response_body = json.dumps(prediction.asnumpy().tolist())

    return response_body, output_content_type


if __name__ == '__main__':
    model_dir = '/home/ubuntu/models/mxnet-gluon-mnist'
    net = model_fn(model_dir)

    import json
    import random
    data = {'inputs': [random.random() for _ in range(784)]}
    data = json.dumps(data)
    
    content_type = 'application/json'
    a, b = transform_fn(net, data, content_type, content_type)
    print(a, b)

