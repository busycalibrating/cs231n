from builtins import range
from builtins import object
import numpy as np
from past.builtins import xrange
import tqdm

class KNearestNeighbor(object):
    """ a kNN classifier with L2 distance """

    def __init__(self):
        pass

    def train(self, X, y):
        """
        Train the classifier. For k-nearest neighbors this is just
        memorizing the training data.

        Inputs:
        - X: A numpy array of shape (num_train, D) containing the training data
          consisting of num_train samples each of dimension D.
        - y: A numpy array of shape (N,) containing the training labels, where
             y[i] is the label for X[i].
        """
        self.X_train = X
        self.y_train = y

    def predict(self, X, k=1, num_loops=0):
        """
        Predict labels for test data using this classifier.

        Inputs:
        - X: A numpy array of shape (num_test, D) containing test data consisting
             of num_test samples each of dimension D.
        - k: The number of nearest neighbors that vote for the predicted labels.
        - num_loops: Determines which implementation to use to compute distances
          between training points and testing points.

        Returns:
        - y: A numpy array of shape (num_test,) containing predicted labels for the
          test data, where y[i] is the predicted label for the test point X[i].
        """
        if num_loops == 0:
            dists = self.compute_distances_no_loops(X)
        elif num_loops == 1:
            dists = self.compute_distances_one_loop(X)
        elif num_loops == 2:
            dists = self.compute_distances_two_loops(X)
        else:
            raise ValueError('Invalid value %d for num_loops' % num_loops)

        return self.predict_labels(dists, k=k)

    def compute_distances_two_loops(self, X):
        """
        Compute the distance between each test point in X and each training point
        in self.X_train using a nested loop over both the training data and the
        test data.

        Inputs:
        - X: A numpy array of shape (num_test, D) containing test data.

        Returns:
        - dists: A numpy array of shape (num_test, num_train) where dists[i, j]
          is the Euclidean distance between the ith test point and the jth training
          point.
        """
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train))
        
        for i in tqdm.tqdm(range(num_test)):

            for j in range(num_train):
                #####################################################################
                # TODO:                                                             #
                # Compute the l2 distance between the ith test point and the jth    #
                # training point, and store the result in dists[i, j]. You should   #
                # not use a loop over dimension, nor use np.linalg.norm().          #
                #####################################################################
                # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

                # L2 distance is defined by sqrt(sum((px1 - px2)^2))
                test_img = X[i]
                train_img = self.X_train[j]

                sum_of_squares_of_diffs = np.sum((test_img - train_img) ** 2)            
                
                dists[i, j] = np.sqrt(sum_of_squares_of_diffs)

                # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        return dists

    def compute_distances_one_loop(self, X):
        """
        Compute the distance between each test point in X and each training point
        in self.X_train using a single loop over the test data.

        Input / Output: Same as compute_distances_two_loops
        """
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train))
        for i in tqdm.tqdm(range(num_test)):
            #######################################################################
            # TODO:                                                               #
            # Compute the l2 distance between the ith test point and all training #
            # points, and store the result in dists[i, :].                        #
            # Do not use np.linalg.norm().                                        #
            #######################################################################
            # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

            # L2 distance is defined by sqrt(sum((px1 - px2)^2))
            # Iterating over each test image we want to compute an array of 1xn (n=# train)
            
            # First, convert it from (3072, ) to (1, 3072)
            test_img = X[i][np.newaxis, :]

            # Let numpy broadcast do stuff (1 -> 5000). axis=1 specifies to sum along the
            # pixel dimension rather than the image dimension (sum all pixels per image vs
            # all images per pixel)
            sum_of_squares_of_diffs = np.sum(np.square(test_img - self.X_train), axis=1)            
            
            # Take the square root in one go, this is a (5000, ) array
            dists[i, :] = np.sqrt(sum_of_squares_of_diffs)            

            # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        return dists


    def compute_distances_no_loops(self, X):
        """
        Compute the distance between each test point in X and each training point
        in self.X_train using no explicit loops.

        Input / Output: Same as compute_distances_two_loops
        """
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train))
        #########################################################################
        # TODO:                                                                 #
        # Compute the l2 distance between all test points and all training      #
        # points without using any explicit loops, and store the result in      #
        # dists.                                                                #
        #                                                                       #
        # You should implement this function using only basic array operations; #
        # in particular you should not use functions from scipy,                #
        # nor use np.linalg.norm().                                             #
        #                                                                       #
        # HINT: Try to formulate the l2 distance using matrix multiplication    #
        #       and two broadcast sums.                                         #
        #########################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        """
        L2 distance is defined by sqrt(sum((px1 - px2)^2))
        
        Expand out the sum: px1^2 + px2^2 - 2*px1*px2
        
        The first two terms can be computed by summing the square of the matrices.
        The cross term can be obtained by doing a matmul on X, X_train.transpose
            (this yields you a (500, 5000) vector.
        Then, sum everything up and take the elementwise squareroot.
        """
             
        # Incoming test data X: (500, 3072)
        # Train data X_train:   (5000, 3072)

        X2 = np.sum(np.square(X), axis=1)
        X_train2 = np.sum(np.square(self.X_train), axis=1)
        cross = 2 * np.matmul(X, self.X_train.T)       
        
        sum_of_squares_of_diffs = X2[:, np.newaxis] + X_train2[np.newaxis, :] - cross

        # Don't do this: this allocates a 8byte * 500 * 5000 * 3072 ~= 61GB array
        # diff = X[:, np.newaxis, :] - self.X_train[np.newaxis, :, :] 

        # Dists will be a (500, 5000) array       
        dists= np.sqrt(sum_of_squares_of_diffs)            


        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        return dists

    def predict_labels(self, dists, k=1):
        """
        Given a matrix of distances between test points and training points,
        predict a label for each test point.

        Inputs:
        - dists: A numpy array of shape (num_test, num_train) where dists[i, j]
          gives the distance betwen the ith test point and the jth training point.

        Returns:
        - y: A numpy array of shape (num_test,) containing predicted labels for the
          test data, where y[i] is the predicted label for the test point X[i].
        """
        num_test = dists.shape[0]
        y_pred = np.zeros(num_test)
        for i in tqdm.tqdm(range(num_test)):
            # A list of length k storing the labels of the k nearest neighbors to
            # the ith test point.
            closest_y = []
            #########################################################################
            # TODO:                                                                 #
            # Use the distance matrix to find the k nearest neighbors of the ith    #
            # testing point, and use self.y_train to find the labels of these       #
            # neighbors. Store these labels in closest_y.                           #
            # Hint: Look up the function numpy.argsort.                             #
            #########################################################################
            # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

            """
            1. Get the entry from the dists array
            2. Use np.argsort to evaluate the ordering of neighbours (w.r.t. l2 distance)
            3. Save the k nearest entries into closest_y 
            """

            # Note that argsort returns a list of indecies, in the correct order
            # to sort the array
            arr = np.argsort(dists[i,:])[0:k]
            closest_y = self.y_train[arr]

            # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
            #########################################################################
            # TODO:                                                                 #
            # Now that you have found the labels of the k nearest neighbors, you    #
            # need to find the most common label in the list closest_y of labels.   #
            # Store this label in y_pred[i]. Break ties by choosing the smaller     #
            # label.                                                                #
            #########################################################################
            # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

            """
            1. Get the counts of each label
            2. Find the indicies corresponding to the maximum counts
            3. Obtain the labels corresponding to the above indicies
            4. Save the minimum value of the set
            """
            unique_labels, counts = np.unique(closest_y, return_counts=True)
            max_index = np.where(counts == counts.max())[0]  # not sure about this [0]
            tied_labels = unique_labels[max_index]
            y_pred[i] = tied_labels.min()

            # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        return y_pred
