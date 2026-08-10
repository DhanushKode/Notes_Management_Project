import random
import string

def generate_otp():
    otp=''
    c_1=[chr(i) for i in range(ord('A'),ord('Z')+1)]
    s_1=[chr(i) for i in range(ord('a'),ord('z')+1)]
    for i in range(2):
        otp = otp+random.choice(c_1)+str(random.randint(0,9))+random.choice(s_1)
    return otp