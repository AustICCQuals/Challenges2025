FLAG = b'oiccflag{??????????????????????????????????????????}'

F = GF(0xdead1337cec2a21ad8d01f0ddabce77f57568d649495236d18df76b5037444b1)
A = random_matrix(F, len(FLAG))[:,:-3]
b = A * random_vector(F, A.ncols()) + vector(F, FLAG) * F.random_element()
save((A, b), "Ab")