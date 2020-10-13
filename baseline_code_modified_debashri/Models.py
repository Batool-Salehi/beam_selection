from __future__ import division

import six
from tensorflow.keras.layers import Activation, BatchNormalization, LeakyReLU, Conv2D, Add,\
    Flatten, MaxPooling2D, Dense, Reshape, Input, Dropout, concatenate, Conv1D, MaxPooling1D
from tensorflow.keras.models import Model, Sequential

from tensorflow.keras import regularizers

#from tensorflow.keras.layers.convolutional import (
#    Conv2D,
#   MaxPooling2D,
#    AveragePooling2D
#)
#from keras.layers.merge import add
from tensorflow.keras.regularizers import l2
from tensorflow.keras import backend as K

# DOUBLED THE NUMBER WITH NEURONS
def Baseline(input_shape, num_classes, strategy, fusion=False):
    dropProb = 0.3
    channel = 16
    input_lid = Input(shape=input_shape, name='img_input')
    layer = Conv2D(channel, kernel_size=(7, 7),
                   activation='relu', padding="SAME", input_shape=input_shape, name='img_conv1')(input_lid)
    layer = Conv2D(channel, (5, 5), padding="SAME", activation='relu', name='img_conv2')(layer)
    layer = Conv2D(channel, (5, 5), padding="SAME", activation='relu', name='img_conv3')(layer)
    layer = MaxPooling2D(pool_size=(2, 2), name='img_maxpool1')(layer)
    layer = Dropout(dropProb, name='img_dropout1')(layer)

    layer = Conv2D(2*channel, (3, 3), padding="SAME", activation='relu', name='img_conv4')(layer)
    layer = Conv2D(2*channel, (3, 3), padding="SAME", activation='relu', name='img_conv5')(layer)
    layer = MaxPooling2D(pool_size=(2, 2), name='img_maxpool2')(layer)
    layer = Dropout(dropProb, name='img_dropout2')(layer)

    layer = Conv2D(4*channel, (3, 3), padding="SAME", activation='relu', name='img_conv6')(layer)
    layer = Conv2D(4*channel, (3, 3), padding="SAME", activation='relu', name='img_conv7')(layer)
    layer = MaxPooling2D(pool_size=(1, 2), name='img_maxpool3')(layer)
    layer = Dropout(dropProb, name='img_dropout3')(layer)

    layer = Conv2D(4*channel, (3, 3), padding="SAME", activation='relu', name='img_conv8')(layer)
    layer = Conv2D(4*channel, (3, 3), padding="SAME", activation='relu', name='img_conv9')(layer)

    layer = Flatten(name='img_flatten')(layer)
    layer = Dense(4*num_classes, activation='relu', name='img_dense1')(layer)
    layer = Dropout(0.5, name='img_dropout4')(layer)
    layer = Dense(2*num_classes, activation='relu', name='img_dense2')(layer)
    out = layer = Dropout(0.5, name='img_dropout5')(layer)
    #out = Dense(num_classes, activation='relu')(layer)  #tanh NOT WORKING

    if fusion: return Model(inputs=input_lid, outputs=out)

    if strategy == 'one_hot':
       out = Dense(num_classes,activation='softmax')(layer)
    elif strategy == 'reg':
       out = Dense(num_classes)(layer)
    return Model(inputs = input_lid, outputs = out)


def ResLike(input_shape, num_classes, strategy, fusion= False):
    dropProb = 0.3
    channel = 32  # 32 now is the best, better than 64, 16
    input_lid = Input(shape=input_shape, name='lidar_input')
    a = layer = Conv2D(channel, kernel_size=(3, 3),
                       activation='relu', padding="SAME", input_shape=input_shape, name='lidar_conv1')(input_lid)
    layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu', name='lidar_conv2')(layer)
    layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu', name='lidar_conv3')(layer)  # + a
    layer = Add(name='lidar_add1')([layer, a])  # DR
    layer = MaxPooling2D(pool_size=(2, 2), name='lidar_maxpool1')(layer)
    b = layer = Dropout(dropProb, name='lidar_dropout1')(layer)

    layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu', name='lidar_conv4')(layer)
    layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu', name='lidar_conv5')(layer)  # + b
    layer = Add(name='lidar_add2')([layer, b])  # DR
    layer = MaxPooling2D(pool_size=(2, 2), name='lidar_maxpool2')(layer)
    c = layer = Dropout(dropProb, name='lidar_dropout2')(layer)

    layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu', name='lidar_conv6')(layer)
    layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu', name='lidar_conv7')(layer)  # + c
    layer = Add(name='lidar_add3')([layer, c])  # DR
    layer = MaxPooling2D(pool_size=(1, 2), name='lidar_maxpool3')(layer)
    d = layer = Dropout(dropProb, name='lidar_dropout3')(layer)

    # if add this layer, need 35 epochs to converge
    # layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu')(layer)
    # layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu')(layer) + d
    # layer = MaxPooling2D(pool_size=(1, 2))(layer)
    # e = layer = Dropout(dropProb)(layer)

    layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu', name='lidar_conv8')(layer)
    layer = Conv2D(channel, (3, 3), padding="SAME", activation='relu', name='lidar_conv9')(layer)  # + d
    layer = Add(name='lidar_add4')([layer, d])  # DR

    layer = Flatten(name='lidar_flatten')(layer)
    layer = Dense(512, activation='relu', kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4), name="lidar_dense1")(layer)
    layer = Dropout(0.2, name='lidar_dropout4')(layer)  # 0.25 is similar ... could try more values
    layer = Dense(256, activation='relu', kernel_regularizer=regularizers.l1_l2(l1=1e-5, l2=1e-4), name="lidar_dense2")(
        layer)
    out = layer = Dropout(0.2, name='lidar_dropout5')(layer)  # 0.25 is similar ... could try more values

    if fusion : return Model(inputs=input_lid, outputs=out)
    if strategy == 'one_hot':
        out = Dense(num_classes, activation='softmax')(layer)
    elif strategy == 'reg':
        out = Dense(num_classes)(layer)
    return Model(inputs=input_lid, outputs=out)