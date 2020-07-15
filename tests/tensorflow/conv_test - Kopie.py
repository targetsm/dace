try:
    import tensorflow as tf
except ImportError:
    print("WARNING: Tensorflow not found, skipping test")
    exit(0)

from tensorflow.python.ops import gen_nn_ops
import numpy as np
import sys
from dace.frontend.tensorflow import TFSession

if __name__ == '__main__':
    gpu = len(sys.argv) == 2 and sys.argv[1] == 'gpu'
    inp_shape = [10, 10, 10, 10]
    filter_shape = [3, 3, 10, 3]
    strides = [1, 3, 3, 1]

    inp = tf.placeholder(tf.float32, inp_shape)
    filter = tf.placeholder(tf.float32, filter_shape)
    outp = tf.nn.conv2d(
        inp, filter, strides, padding="SAME", data_format="NHWC")

    test_in = np.random.uniform(size=tuple(inp_shape)).astype(np.float32)
    test_filter = np.random.uniform(size=tuple(filter_shape)).astype(
        np.float32)

    sess_dace = TFSession()
    sess_tf = tf.Session()

    output_dace = sess_dace.run(
        outp, feed_dict={
            inp: test_in,
            filter: test_filter
        },gpu=gpu)
    output_tf = sess_tf.run(
        outp, feed_dict={
            inp: test_in,
            filter: test_filter
        })
    
    try:
        assert tf.norm(output_dace - output_tf).eval(session=sess_tf) < 1e-3
    except:
        print(output_tf)
        print(output_dace)
        print(tf.linalg.norm(output_tf - output_dace).eval(session=sess_tf))
        raise AssertionError("Convolution test failed")
    ##### Conv backprop grad ######
    inp_shape = [10, 10, 10, 10]
    filters = [[2, 2, 10, 3]]
    strides = [[1, 3, 3, 1]]
    paddings = ["VALID"]
    for p in paddings:
        for f in filters:
            for s in strides:
                print(p, f, s)
                filter = tf.placeholder(tf.float32, f)
                outp = tf.nn.conv2d(
                    inp, filter, s, padding=p, data_format="NHWC")
                out_backprop = tf.placeholder(tf.float32, outp.shape)
                inp_gradients = gen_nn_ops.conv2d_backprop_input(
                    inp_shape, filter, out_backprop, s, padding=p)
                test_grads = np.random.uniform(size=outp.shape).astype(
                    np.float32)
                test_filter = np.random.uniform(size=tuple(f)).astype(
                    np.float32)

                output_tf = sess_tf.run(
                    inp_gradients,
                    feed_dict={
                        filter: test_filter,
                        out_backprop: test_grads
                    })
                output_dace = sess_dace.run(
                    inp_gradients,
                    feed_dict={
                        filter: test_filter,
                        out_backprop: test_grads
                    },gpu=gpu)

                try:
                    assert tf.norm(output_dace -
                                   output_tf).eval(session=sess_tf) < 1e-3
                except:
                    print(p)
                    print(f)
                    print(s)
                    print(output_tf)
                    print(output_dace)
                    print(
                        tf.linalg.norm(output_tf -
                                       output_dace).eval(session=sess_tf))
                    raise AssertionError("Convolution grad test failed")

    ##### Conv filter backprop ##################
    inp_shape = [10, 10, 10, 10]
    filters = [[4, 4, 10, 3]]
    strides = [[1, 1, 1, 1]]
    paddings = ["SAME"]
    for p in paddings:
        for f in filters:
            for s in strides:
                input_placeholder = tf.placeholder(tf.float32, inp_shape)
                filter = tf.placeholder(tf.float32, f)
                outp = tf.nn.conv2d(
                    inp, filter, s, padding=p, data_format="NHWC")
                out_backprop = tf.placeholder(tf.float32, outp.shape)
                filter_gradients = gen_nn_ops.conv2d_backprop_filter(
                    input_placeholder, f, out_backprop, s, padding=p)
                test_grads = np.random.uniform(size=outp.shape).astype(
                    np.float32)
                test_input = np.random.uniform(size=tuple(inp_shape)).astype(
                    np.float32)

                output_tf = sess_tf.run(
                    filter_gradients,
                    feed_dict={
                        input_placeholder: test_input,
                        out_backprop: test_grads
                    })
                output_dace = sess_dace.run(
                    filter_gradients,
                    feed_dict={
                        input_placeholder: test_input,
                        out_backprop: test_grads
                    },gpu=gpu)

                try:
                    assert tf.norm(output_dace -
                                   output_tf).eval(session=sess_tf) < 1e-3
                except:
                    print(p)
                    print(f)
                    print(s)
                    print(output_tf)
                    print(output_dace)
                    print(
                        tf.linalg.norm(output_tf -
                                       output_dace).eval(session=sess_tf))
                    raise AssertionError("Convolution filter grad test failed")
