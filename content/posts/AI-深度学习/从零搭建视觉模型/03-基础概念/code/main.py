"""跟踪像素、轴与拷贝。运行方式与练习见 README.md。"""
import copy
# 两行三列，每个像素含 RGB 三个通道。
hwc = [[[255,0,0],[0,255,0],[0,0,255]],
       [[255,255,255],[0,0,0],[255,128,0]]]
chw = [[[hwc[y][x][c]/255 for x in range(3)] for y in range(2)] for c in range(3)]
nchw = [chw]
print('HWC=(2,3,3), CHW=(3,2,3), NCHW=(1,3,2,3)')
print('橙色像素:', [nchw[0][c][1][2] for c in range(3)])
assert nchw[0][1][1][2] == 128/255
alias = hwc
clone = copy.deepcopy(hwc)
alias[0][0][0] = 0
assert hwc[0][0][0] == 0 and clone[0][0][0] == 255
print('共享引用会修改原对象，deepcopy 保留原始值')
