import os
import cv2
import tensorflow as tf
import input_data

# build a simple LeNet-5 for recognition
model_dir = './model/singleLabel'
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
#model_path = os.path.join(model_dir, 'simple_cnn.ckpt')
max_iter = 10000
display_step = 10

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1,1,1,1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1,2,2,1], 
            strides=[1,2,2,1], padding='SAME')

def train():
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
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(y_conv, y_)
    cross_entropy = tf.reduce_mean(cross_entropy)
    train_step = tf.train.AdamOptimizer(1e-3).minimize(cross_entropy)

    correct_prediction = tf.equal(tf.arg_max(y_conv, 1), y_)
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    print ('fetching data...')
    image_batch, label_batch = input_data.data_input('train')

    init = tf.global_variables_initializer()
    saver = tf.train.Saver()

    # train with session
    with tf.Session() as sess:
        #sess.run(init)
        saver.restore(sess, './model/backup/9999/simple_cnn.ckpt')
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(sess=sess,coord=coord)
        print ('start training...')
        for i in xrange(max_iter):
            val, l = sess.run([image_batch, label_batch])
            _, loss = sess.run([train_step, cross_entropy], feed_dict=
                    {x_image: val, y_: l, keep_prob: 0.5})

            # display
            if i % display_step == 0:
                train_accuracy= accuracy.eval(feed_dict=
                        {x_image:val, y_:l, keep_prob: 1.0})
                print ('step {}, training accuracy {}, loss {}'.format(i, train_accuracy, loss))

            # save model per 1000 iters
            if i % 1000 == 0 or (i + 1) == max_iter:
                sep_dir = os.path.join(model_dir, str(i))
                if not os.path.exists(sep_dir):
                    os.makedirs(sep_dir)
                print ('save the model to {}'.format(sep_dir))
                model_path = os.path.join(sep_dir, 'simple_cnn.ckpt')
                saver.save(sess, model_path)

        #print ('save the model to {}'.format(model_dir))
        #saver.save(sess, model_path)

        coord.request_stop()
        coord.join(threads)
        print ('Finish training')

if __name__ == '__main__':
    train()
