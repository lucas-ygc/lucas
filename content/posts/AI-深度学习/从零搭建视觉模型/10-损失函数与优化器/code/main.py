"""交叉熵梯度与一次 SGD 更新。运行方式与练习见 README.md。"""
import torch
import torch.nn.functional as F
torch.set_num_threads(2)
logits = torch.tensor([[2.,1.]], requires_grad=True)
target = torch.tensor([1])
loss = F.cross_entropy(logits, target)
manual = -torch.log_softmax(logits, dim=1)[0,1]
torch.testing.assert_close(loss, manual)
loss.backward()
expected_grad = logits.detach().softmax(1) - F.one_hot(target,2)
torch.testing.assert_close(logits.grad, expected_grad)
print('loss:', loss.item(), 'gradient:', logits.grad.tolist())
with torch.no_grad(): updated = logits - 0.1 * logits.grad
new_loss = F.cross_entropy(updated, target)
assert new_loss < loss
print('更新后的 loss:', new_loss.item())
