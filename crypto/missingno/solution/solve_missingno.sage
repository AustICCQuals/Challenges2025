A,b = load("Ab")
Ab = block_matrix([[x.matrix() for x in row] for row in A.augment(b)])
K = Ab.delete_rows(range(0, Ab.nrows(), 6)).right_kernel_matrix()
M = matrix(A.nrows(), A.nrows(), b[0].parent().characteristic())
M[:K.nrows()] = (K * Ab[::6].T).rref()
v = M.BKZ()[0]
print(bytes(v * sgn(v[0])))
# b'oiccflag{using_LLL_to_beat_MissingNo_is_peak_crypto}'