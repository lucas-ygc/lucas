"""输入颜色契约与队列延迟。运行方式与练习见 README.md。"""
import math
# 离线单像素帧，不访问摄像头；BGR 红色应转成 RGB 的 [1,0,0]。
bgr = [0,0,255]
rgb = list(reversed(bgr))
normalized = [v/255 for v in rgb]
assert normalized == [1.0,0.0,0.0]
print('RGB:',normalized)
# 确定性离散事件模拟：每 33ms 来一帧，每次推理耗时 50ms。
arrivals = list(range(0,3300,33))
def simulate(latest):
    now, i, latencies, dropped = 0,0,[],0
    while i<len(arrivals):
        now = max(now,arrivals[i])
        chosen = i
        if latest:
            while chosen+1<len(arrivals) and arrivals[chosen+1]<=now: chosen += 1
        dropped += chosen-i
        now += 50
        latencies.append(now-arrivals[chosen])
        i = chosen+1
    ordered = sorted(latencies)
    return len(latencies),dropped,sum(latencies)/len(latencies),ordered[math.ceil(.95*len(ordered))-1]
fifo,latest = simulate(False),simulate(True)
print('策略: 完成数/丢帧数/平均延迟/P95毫秒')
print('FIFO:',fifo,'保留最新:',latest)
assert latest[3]<fifo[3]
assert latest[0]+latest[1]==len(arrivals)
