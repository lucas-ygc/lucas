"""批次计数与加权平均。运行方式与练习见 README.md。"""
import math
size, batch, epochs = 103, 32, 3
batches = [min(batch,size-i) for i in range(0,size,batch)]
means = [1.0,0.8,0.6,2.0]
weighted = sum(n*v for n,v in zip(batches,means))/size
naive = sum(means)/len(means)
assert batches == [32,32,32,7]
assert math.ceil(size/batch)*epochs == 12
print('batch sizes:',batches,'updates:',len(batches)*epochs)
print('样本加权损失:',weighted,'批次直接平均:',naive)
for epoch in range(epochs): print('epoch',epoch+1,'lr',0.1*0.5**epoch)
