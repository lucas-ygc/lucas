"""区分任务、结构与学习方式。运行方式与练习见 README.md。"""
# 教学分类表，不作为当前模型排名；结构不唯一决定任务。
models = [
 {'name':'TinyCNN','task':'classification','structure':'CNN','learning':'supervised'},
 {'name':'ResNet classifier','task':'classification','structure':'CNN','learning':'supervised'},
 {'name':'U-Net','task':'segmentation','structure':'encoder-decoder','learning':'supervised'},
 {'name':'ViT classifier','task':'classification','structure':'Transformer','learning':'supervised'},
]
for axis in ['task','structure','learning']:
    groups = {}
    for row in models: groups.setdefault(row[axis],[]).append(row['name'])
    print(axis,groups)
classifiers = [row for row in models if row['task']=='classification']
assert len({row['structure'] for row in classifiers})==2
print('分类任务可以使用 CNN 或 Transformer；表中的学习方式仅指本例训练配置。')
