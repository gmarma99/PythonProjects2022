import random, hashlib

am=input("Enter your ID: ")

tmp=hashlib.sha256(am.encode()).hexdigest()

seed=int(tmp,16)

random.seed(seed)

lst=list(range(1,13))

random.shuffle(lst)

print(lst[:4])

input()