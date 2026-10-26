"""普通卷积与深度可分离卷积成本。运行方式与练习见 README.md。"""
cin,cout,k,h,w = 32,64,3,32,32
regular = cin*cout*k*k
separable = cin*k*k+cin*cout
print('不含 bias 参数:',regular,separable)
print('MACs:',regular*h*w,separable*h*w)
print('参数比例:',separable/regular)
print('FP32 输出激活字节:',cout*h*w*4)
assert regular == 18432 and separable == 2336
assert regular*h*w == 18874368
# MAC 一次乘加按一个单位；若将乘与加各算一次，FLOPs 约为两倍。
