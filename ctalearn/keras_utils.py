#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 09:26:11 2018

@author: jsevillamol
"""

import functools
import numpy as np
import tensorflow as tf
from tensorflow.python.keras import metrics
import tensorflow.keras.backend as K

# metrics

def as_keras_metric(method):
    
    @functools.wraps(method)
    def wrapper(self, args, **kwargs):
        """ Wrapper for turning tensorflow metrics into keras metrics """
        value, update_op = method(self, args, **kwargs)
        tf.keras.backend.get_session().run(tf.local_variables_initializer())
        with tf.control_dependencies([update_op]):
            value = tf.identity(value)
        return value
    return wrapper

auroc = as_keras_metric(tf.metrics.auc)


# taken from https://stackoverflow.com/questions/42606207/keras-custom-decision-threshold-for-precision-and-recall
def precision_threshold(threshold=0.5):
    def precision(y_true, y_pred):
        """Precision metric.
        Computes the precision over the whole batch using threshold_value.
        """
        threshold_value = threshold
        # Adaptation of the "round()" used before to get the predictions. Clipping to make sure that the predicted raw values are between 0 and 1.
        y_pred = K.cast(K.greater(K.clip(y_pred, 0, 1), threshold_value), K.floatx())
        # Compute the number of true positives. Rounding in prevention to make sure we have an integer.
        true_positives = K.round(K.sum(K.clip(y_true * y_pred, 0, 1)))
        # count the predicted positives
        predicted_positives = K.sum(y_pred)
        # Get the precision ratio
        precision_ratio = true_positives / (predicted_positives + K.epsilon())
        return precision_ratio
    return precision

def recall_threshold(threshold = 0.5):
    def recall(y_true, y_pred):
        """Recall metric.
        Computes the recall over the whole batch using threshold_value.
        """
        threshold_value = threshold
        # Adaptation of the "round()" used before to get the predictions. Clipping to make sure that the predicted raw values are between 0 and 1.
        y_pred = K.cast(K.greater(K.clip(y_pred, 0, 1), threshold_value), K.floatx())
        # Compute the number of true positives. Rounding in prevention to make sure we have an integer.
        true_positives = K.round(K.sum(K.clip(y_true * y_pred, 0, 1)))
        # Compute the number of positive targets.
        possible_positives = K.sum(K.clip(y_true, 0, 1))
        recall_ratio = true_positives / (possible_positives + K.epsilon())
        return recall_ratio
    return recall
    
# QUICK TESTS
if __name__ == "__main__":
    precision = precision_threshold()
    recall = recall_threshold()

    y_true = np.zeros(shape=(4,2))
    y_true[:, 0] = [1,0,1,0]
    y_true[:, 1] = [0,1,0,1]
    
    y_pred1 = np.zeros(shape=(4,2))
    y_pred1[:, 0] = [1,0,1,0]
    y_pred1[:, 1] = [0,1,0,1]
    
    print(K.eval(metrics.categorical_accuracy(y_true, y_pred1)))
    print(K.eval(auroc(y_true, y_pred1)))
    print(K.eval(precision(y_true, y_pred1)))
    print(K.eval(recall(y_true, y_pred1)))
    
    y_pred2 = np.zeros(shape=(4,2))
    y_pred2[:, 0] = [0,1,0,1]
    y_pred2[:, 1] = [1,0,1,0]
    
    print(K.eval(metrics.categorical_accuracy(y_true, y_pred2)))
    print(K.eval(auroc(y_true, y_pred2)))
    print(K.eval(precision(y_true, y_pred2)))
    print(K.eval(recall(y_true, y_pred2)))
    