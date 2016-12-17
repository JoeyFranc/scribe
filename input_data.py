import cv2
import tensorflow as tf

def read_decode(filename):
    filename_queue = tf.train.string_input_producer([filename])

    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    features = tf.parse_single_example(serialized_example, features={
        'label': tf.FixedLenFeature([], tf.int64),
        'img_raw': tf.FixedLenFeature([], tf.string)
    })

    img = tf.decode_raw(features['img_raw'], tf.uint8)
    img = tf.reshape(img, [128, 128, 1])
    img = tf.cast(img, tf.float32) * (1. / 255) - 0.5
    label = tf.cast(features['label'], tf.int64)

    return img, label

def data_input(phase):
    image, label = read_decode('./robustSet/singleLabel/{}.tfrecords'.format(phase))
    print ('input {} data'.format(phase))
    if phase == 'train':
        img_batch, label_batch = tf.train.shuffle_batch(
                [image,label],batch_size=100, num_threads=2,
                capacity=4000, min_after_dequeue=2000)
    else:
        img_batch, label_batch = tf.train.batch(
                [image,label],batch_size=100,
                capacity=4000)

    return img_batch, label_batch

