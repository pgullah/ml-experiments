

# Z = Sum(Xi * Wi) = X1 * W1 + X2 * W2 + .... + Xn * Wn

import time
import numpy as np

def timeit():
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"Execution time of {func.__name__}: {end_time - start_time:.6f} seconds")
            return result
        return wrapper
    return decorator

@timeit()
def python_dot_product(x, w):
    z = 0.
    for i in range(len(x)):
        z += x[i] * w[i]
    return z

@timeit()
def numpy_dotproduct(x, w):
    # same as np.dot(x, w)
    # and same as x @ w
    return x.dot(w)
    

def compare_dot_product():
    print("Hello from numpy-learning!")
    print("\n##### Python Dot Product ####")
    a = [1., 2., 3.]
    b = [4., 5., 6.]
    print(python_dot_product(a, b))
    print("\n ### Large sum ")
    large_a = list(range(100000000))
    large_b = list(range(100000000))
    print(python_dot_product(large_a, large_b))
    print("\n #### Numpy Sum of X * W ####")
    large_a = np.array(large_a)
    large_b = np.array(large_b)
    print(numpy_dotproduct(large_a, large_b))


if __name__ == "__main__":
    # compare_dot_product()
    a = np.array([1., 2., 3.,])
    print("1D Array (aka Vector): \n", a)
    print("array type:", a.dtype)
    print("array shape:", a.shape)
    print("array size:", a.size)
    print("array dim:", a.ndim)
    
    lst = [
       [1, 2, 3,3], 
       [4, 5, 6,4]
    ]
    ary2d = np.array(lst)
    print("2D Array (aka Matrix): \n", ary2d)
    print("array type:", ary2d.dtype)
    print("array shape:", ary2d.shape)
    print("array dim:", ary2d.ndim)
    
    var_list = [
        [1,2,3],
        [4],
        [5,6],
        []
    ]
    try:
        jagged_array = np.array(var_list)
        print("jagged array: \n", jagged_array)
        print("jagged array type: ", jagged_array.dtype)
        print("jagged array shape: ", jagged_array.shape)
        print("jagged array shape: ", jagged_array.ndim)
    except Exception as e:
        print("Jagged array creation failed: ", e)

    non_homogenous_array = np.array([1, 'a', 2., 3, 'dfsdfs', True, 4.5, .7, False])
    print("non homogenous array type ", non_homogenous_array.dtype)
    try:
        non_homogenous_array.astype(np.float32)
    except Exception as e:
        print("Non homogenesou array convertion failed: ", e)
        
    print('array witg explicit type: ', np.array([1, 2, 3], dtype=np.float32).shape)
    print('array witg explicit type: ', np.array([1, 2, 3], dtype=np.int32))
    print('array witg explicit type: ', np.array([1, 2, 3], dtype=np.int64))
    print('array witg explicit type: ', np.array([1, 2, 3], dtype=np.float64))
    
    ones = np.ones((3, 4), dtype=np.int32)
    print("ones array: \n", ones)
    zeros = np.zeros((3, 4), dtype=np.float32)
    print("zeros array: \n", zeros)
    
    print("Addiition: zeros  :\n", zeros + 3)
    print("Substraction: \n", zeros - 3)
    print("Multiplication: \n", (zeros + 4 )* 3)
    
    # identity
    print("np eye: \n", np.eye(2,2, dtype=np.int32))
    print("np eye: \n", np.eye(2,2,) == np.eye(2))
    print("np eye: \n", np.eye(2, dtype=np.int32))
    
    print("np diagonal: \n", np.diag((1,2,3)))
    print("np diagonal: \n", np.diag((1,1,1)))
    
    print("np arange (aka range): \n", np.arange(5))
    print("np arange (aka range): \n", np.arange(-5))
    print("np arange (aka range): \n", np.arange(-5, 5))
    print("np arange (aka range): \n", np.arange(4, 10))
    print("np arrange with step 2: \n", np.arange(14, step=2))
    print("np arrange with step 0.1: \n", np.arange(1., 11., 0.1))
    for i in range(0,11):
        print(f"np linear space [{i}]: \n", np.linspace(6., 15., num=i))
        
    ary = np.array([1, 2, 3])
    print('array index: ', ary[0])
    print("array index: ", ary[2])
    print("array index: ", ary[-1])
    print("array index: ", ary[-3])
    try:
        print("array index: ", ary[-4])
    except:
        print("array index: ", "Index out of bounds")
        
    print("array slice: ", ary[0:2])
    ary = np.array([[1, 2, 3],
                [4, 5, 6]])
    print("multi dimensional array slice: ", ary[1, 2])
    print("multi dimensional array slice: ", ary[0, -2])
    print("multi dimensional array slice: ", ary[-1, -1])
    print("Entire first column: ", ary[:, 0])
    print("Entire second column: ", ary[:, 1])
    print("First two columns: ", ary[:,:2])
    
    
    lst = [[1, 2, 3], 
       [4, 5, 6]] # 2d array

    print("\n #### pythonic array addition")
    for row_idx, row_val in enumerate(lst):
        for col_idx, col_val in enumerate(row_val):
            lst[row_idx][col_idx] += 1
    print("list lst:", lst)
    
    lst = [[1, 2, 3], [4, 5, 6]]
    print("\n #### pythonic array addition using list comprehension")
    lst = [[cell + 1 for cell in row] for row in lst]
    print("list lst:", lst)
    
    print("\n #### numpy array addition using u(niversal)funcs")
    ary = np.array([[1, 2, 3], [4, 5, 6]])
    print("numpy array lst:", np.add(ary, 1) )
    print("numpy array lst:", ary + 1)
    print("numpy array power:", np.power(ary, 2))
    print("numpy array power:", ary ** 2)
    print("numpy reduce with axis 0: ", np.add.reduce(ary, axis=0))
    print("numpy reduce with axis 1: ", np.add.reduce(ary, axis=1))
    print("numpy sum: ", np.sum(ary, axis=0))
    print("numpy sum: ", np.sum(ary, axis=1))
    print("numpy sum: ", np.sum(ary))
    
    print("\n #### numpy array multiplication using u(niversal)funcs")
    ary = np.array([[1, 2, 3], [4, 5, 6]])
    print("numpy array lst:", np.multiply(ary, 2) )
    
    print("\n #### numpy array broadcasting")
    ary = np.array([1, 2, 3])
    print("numpy array lst:", ary + 1)
    print("array + another array", np.array([1, 2, 3]) + np.array([1, 1, 1]))
    print("Non homogeneous array add:", np.array([[1, 2, 3], [4, 5, 6]]) + np.array([1, 2, 3]))
    
    print("\n #### numpy array advanced indexing")
    ary = np.array([[1, 2, 3],
                [4, 5, 6]])
    first_row = ary[0]
    print("first row:", first_row)
    first_row += 99
    print("first row after modification:", first_row)
    print("Original array after modification:", ary)
    
    print("\n #### numpy array advanced indexing ")
    ary = np.array([[1, 2, 3],
                [4, 5, 6]])
    first_row = ary[:, [0, 2]] 
    first_row += 99
    print("first row after modification:", first_row)
    print("Original array after modification:", ary)
    
    print("\n #### numpy array boolean masking")
    ary = np.array([[1, 2, 3],
                [4, 5, 6]])
    greater3_mask = ary > 3
    print("mask:", greater3_mask)
    print("Array with mask:", ary[greater3_mask])
    print("Complex mask:", ary[(ary > 3) & (ary < 6)])
    
    print("\n #### numpy array random")
    print("randome with seed:", np.random.seed(123))
    print("randome with same seed:", np.random.rand(3))
    print("randome with same seed:", np.random.rand(3))
    
    print("\n ### Linear algebra")
    row_vector = np.array([1, 2, 3])
    print("row vector:", row_vector)
    # signatue: reshape(rows, columns)
    # reshape(-1, 1) means that we want to reshape the array into a column vector with an unspecified number of rows 
    # (the -1 indicates that the number of rows should be inferred from the length of the array and the specified number of columns).
    print("column vector:", np.array([1, 2, 3]).reshape(-1, 1))
    print("column vector with multiple dimesnions:", np.array([1, 2, 3]).reshape(1, -1))
    print('Row vector afer: ', row_vector)
    
    

    

    
