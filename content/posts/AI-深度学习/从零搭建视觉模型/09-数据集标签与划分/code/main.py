"""按来源分组划分数据。运行方式与练习见 README.md。"""
import random
# 同一来源的两帧必须一起分配；构造清单不含真实图片。
samples = [{'id':f'{c}-{g}-{f}', 'label':c, 'group':f'{c}-{g}'}
           for c in range(2) for g in range(10) for f in range(2)]
# print(f"{samples}")
print(f"{samples[0]}")
splits = {name:[] for name in ['train','val','test']}
print(f"{splits.keys()}")
print(f"{splits.values()}")
print(f"{splits.items()}")
for label in range(2):
    groups = sorted({s['group'] for s in samples if s['label']==label})
    print(f'类别 {label} 的来源组: {groups}')
    random.Random(7+label).shuffle(groups)
    print(f'类别 {label} 的来源组: {groups}')
    for name, chosen in zip(splits, [groups[:6],groups[6:8],groups[8:]]):
        splits[name].extend(s for s in samples if s['group'] in chosen)
print(f"{splits}")
print(f"{splits.values()}")
group_sets = [{s['group'] for s in rows} for rows in splits.values()]
for i in range(3):
    for j in range(i): assert group_sets[i].isdisjoint(group_sets[j])
assert sum(map(len,splits.values())) == len(samples)
for name, rows in splits.items():
    print(name, len(rows), '类别计数', [sum(s['label']==c for s in rows) for c in range(2)])
