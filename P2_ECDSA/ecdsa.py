# CS 4501: Cryptocurrency
# P2: ECDSA
# Yannie Wu, ylw4sj

import sys
import random

# Finite field operations
def add(x, y, p):
	return (x + y ) % p

def sub(x, y, p):
	num = x + add_inverse(y, p)

	if num >= 0:
		return (x + add_inverse(y, p)) % p
	else:
		return p - ((-1 * num) % p)

def mult(x, y, p):
	return (x * y) % p

def div(x, y, p):
	return x * mult_inverse(y, p) % p

def exp(x, y, p):
	return (x**y) % p

def add_inverse(x, p):
	return (p - x)

def mult_inverse(x, p):
	return (x**(p - 2)) % p

# Elliptic curve operations
def ec_add_one(x, y, p): # Addition of a point to itself (Q = P + P)

	m = div(mult(3, exp(x, 2, p), p), mult(2, y, p), p) # m = 3x^2/2y
	x2 = sub(sub(exp(m, 2, p), x, p), x, p)
	y2 = sub((mult(m, sub(x, x2, p), p)), y, p)
	return x2, y2

def ec_add_two(x1, y1, x2, y2, p): # Addition of two different points (P = Q + R)
	# Point at infinity 
	if (x1, y1) ==(0,0):  # 0 + P = P
		return x2, y2
	if (x2, y2) == (0,0): # 0 + P = P
		return x1, y1
	if (x1==x2) and ((y2 == p-y1) or (y1 == p-y2)): # P + P' = 0
		return 0, 0

	m = div(sub(y2, y1, p), sub(x2, x1, p), p) # m = y2-y1/x2-x1
	x3 = sub(sub(exp(m, 2, p), x1, p), x2, p)
	y3 = sub((mult(m, sub(x1, x3, p), p)), y1, p)
	return x3, y3

def binary_exponents(x): # Helper method for ec_mult
    powers = []
    i = 1
    counter = 0
    while i <= x:
        if i & x:
            powers.append(counter)
        i <<= 1
        counter += 1
    return powers

def ec_mult(x, y, p, o, k): # K * G
	# Compute powers of G
	exponents = binary_exponents(k)
	powers_of_g = [(x, y)]
	curr_exponent = 0

	while curr_exponent <= max(exponents):
		powers_of_g.append(ec_add_one(powers_of_g[curr_exponent][0], powers_of_g[curr_exponent][1], p))
		curr_exponent += 1

	# Add
	x_ans, y_ans = None, None
	for i in exponents:
		if x_ans == None:
			x_ans, y_ans = powers_of_g[exponents[0]]
		else:
			x_ans, y_ans = ec_add_two(x_ans, y_ans, powers_of_g[i][0], powers_of_g[i][1], p)
	
	return x_ans, y_ans

def user_id():
	print('ylw4sj')

def genkey(p, o, gx, gy):
	d = random.randint(1, o - 1) # private key 
	qx, qy = ec_mult(gx, gy, p, o, d) # public key (Q = d * G)
	print(d)
	print(qx)
	print(qy)

def sign(p, o, gx, gy, d, h):
	r = 0
	s = 0
	while (r == 0) or (s == 0):
		k = random.randint(1, o - 1)
		k_inverse = mult_inverse(k, o)
		rx, ry = ec_mult(gx, gy, p, o, k) 
		r = rx
		s = mult(k_inverse, add(h, mult(r, d, o), o), o) % o
	
	print(r)
	print(s)

def verify(p, o, gx, gy, qx, qy, r, s, h):
	s_inverse = mult_inverse(s, o)

	k1 = mult(s_inverse, h, o)
	k2 =  mult(s_inverse, r, o)

	x1, y1 = ec_mult(gx, gy, p, o, k1)
	x2, y2 = ec_mult(qx, qy, p, o, k2)

	rx, ry = ec_add_two(x1, y1, x2, y2, p)

	if rx == r:
		print('True')
	else:
		print('False')

# Helper method to convert additional args to int
def my_function(arg1, *args):
    int_args = [int(arg) for arg in args]  # Convert all arguments to integers
    result = globals()[arg1](*int_args)  # Call the function with integer arguments
    return result

if __name__ == '__main__':
	args = sys.argv
	function_name = args[1]
	my_function(function_name, *args[2:])

