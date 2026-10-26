"""量化舍入、截断与误差。运行方式与练习见 README.md。"""
values = [-2.0,-0.8,0.0,0.3,0.9,2.0]
def quantize(xs,scale):
    q = [max(-127,min(127,round(x/scale))) for x in xs]
    restored = [v*scale for v in q]
    error = max(abs(a-b) for a,b in zip(xs,restored))
    clipped = sum(abs(x/scale)>127 for x in xs)
    return q,restored,error,clipped
for limit in [1.0,2.0]:
    q,restored,error,clipped = quantize(values,limit/127)
    print('校准范围:',(-limit,limit),'整数:',q,'反量化:',restored,'最大误差:',error,'截断数:',clipped)
    if limit==2.0: assert error <= (limit/127)/2 + 1e-12 and clipped==0
    else: assert clipped==2 and error==1.0
