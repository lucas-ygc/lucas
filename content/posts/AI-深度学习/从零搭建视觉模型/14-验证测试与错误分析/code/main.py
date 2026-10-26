"""混淆矩阵与阈值比较。运行方式与练习见 README.md。"""
labels = [0,0,0,1,1,1]
scores = [0.1,0.4,0.8,0.3,0.7,0.9]  # 第 1 类分数，构造样本
for threshold in [0.5,0.75]:
    matrix = [[0,0],[0,0]]
    for truth,score in zip(labels,scores): matrix[truth][int(score>=threshold)] += 1
    tn,fp = matrix[0]; fn,tp = matrix[1]
    precision = tp/(tp+fp) if tp+fp else None
    recall = tp/(tp+fn) if tp+fn else None
    print('threshold:',threshold,'matrix:',matrix,'precision:',precision,'recall:',recall)
    assert sum(map(sum,matrix)) == len(labels)
    if threshold == 0.5: assert matrix == [[2,1],[1,2]]
