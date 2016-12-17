import os
import tensorflow as tf
import numpy as np
import input_data
import math
from train import *

def test():
    # conv layer-1
    W_conv1 = weight_variable([5,5,1,32])
    b_conv1 = bias_variable([32])

    x = tf.placeholder(tf.float32, [None, 16384])
    x_image = tf.reshape(x, [-1, 128, 128, 1])

    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    # conv layer-2
    W_conv2 = weight_variable([5,5,32,64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    # fully-connected
    W_fc1 = weight_variable([32*32*64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 32*32*64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    # dropout
    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    # output layer
    W_fc2 = weight_variable([1024,62])
    b_fc2 = bias_variable([62])

    y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
    y_ = tf.placeholder(tf.int64, [None,])

    # model training
    correct_prediction = tf.equal(tf.arg_max(y_conv, 1), y_)
    #accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    print ('fetching data...')
    image_batch, label_batch = input_data.data_input('test')
    saver = tf.train.Saver()
    
    with tf.Session() as sess:
        saver.restore(sess, './model/singleLabel/9000/simple_cnn.ckpt')
        coord = tf.train.Coordinator()
        try:
            threads = tf.train.start_queue_runners(sess=sess,coord=coord)
            num_iter = int(math.ceil(600*62 / 100))
            print num_iter
            true_count = 0
            total_count = num_iter * 100
            step = 0
            while step < num_iter and not coord.should_stop():
                val, l = sess.run([image_batch, label_batch])
                print step
                p = sess.run([correct_prediction],feed_dict={
                    x_image: val, y_: l, keep_prob: 1.0})
                true_count += np.sum(p)
                step += 1
                print float(true_count) / (step * 100)

            print float(true_count) / total_count
        except Exception as e:
            print e
            print float(true_count) / (step * 100)
            pass

        coord.request_stop()
        coord.join(threads)

test()
