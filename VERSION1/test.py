from main import *
a = [19.8895027624,
6.91138074029,
1.84176195227,
2.59852750108,
4.36081724945,
5.35188654001,
4.96770988574,
2.39961606143,
3.93442622951,
3.56991075223,
4.60279577225,
4.30004777831,
4.76400529334]

results = getDeltaAndStddev(a)

print np.std(np.array(a))
