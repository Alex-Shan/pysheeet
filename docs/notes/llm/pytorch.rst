.. meta::
    :description lang=zh_CN: PyTorch 速查表涵盖 tensors、操作、梯度、GPU 用法、神经网络和 NumPy 互操作性
    :keywords: Python, Python3, PyTorch, tensor, deep learning, GPU, CUDA, gradient, autograd, numpy, neural network

======================================
PyTorch 框架（PyTorch）
======================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

PyTorch是Meta AI开发的开源机器学习框架。它为构建和训练神经网络提供了灵活直观的界面，并具有强大的 GPU 加速支持。 PyTorch使用动态计算图，与静态图框架相比，更容易调试和试验不同的模型架构。

检查CUDA（Check CUDA）
------------------------------------

在运行 GPU 加速计算之前，请验证 CUDA 是否已正确安装且可访问。这些命令有助于检查 GPU 可用性并配置设备设置。

.. code-block:: python

    >>> import torch
    >>> torch.cuda.is_available()
    True
    >>> torch.cuda.nccl.version()
    (2, 26, 2)
    >>> torch.cuda.device_count()
    2
    >>> torch.cuda.get_device_name(0)
    'NVIDIA GeForce RTX 3090'
    >>> torch.cuda.set_device(0)
    >>> torch.cuda.current_device()
    0

检查设备（Check Device）
------------------------------------

确定 tensor 的存储位置（CPU 或 GPU），以确保计算在预期设备上运行。

.. code-block:: python

    >>> tensor = torch.tensor([0, 1, 2, 3, 4, 5])
    >>> tensor.device
    device(type='cpu')
    >>> tensor = tensor.to('cuda')
    >>> tensor.device
    device(type='cuda', index=0)

创建张量（Create Tensors）
----------------------------------------

Tensors是PyTorch中的基本数据结构，类似于NumPy arrays，但具有GPU加速支持。您可以从 Python lists 创建 tensors，使用特定的 values，或使用各种初始化 methods。

.. code-block:: python

    >>> x = torch.tensor([0, 1, 2, 3, 4, 5])
    >>> x = torch.empty(2, 2)
    >>> x = torch.rand(2, 2)
    >>> x = torch.randn(2, 2)
    >>> x = torch.ones(2, 2)
    >>> x = torch.zeros(2, 2)
    >>> x = torch.arange(0, 10, 2)
    >>> x = torch.linspace(0, 1, 5)

    >>> device = torch.device("cuda:0")
    >>> x = torch.tensor([1, 2, 3, 4, 5], device=device)
    >>> x
    tensor([1, 2, 3, 4, 5], device='cuda:0')

张量属性（Tensor Properties）
----------------------------------------------

了解 tensor properties（如 shape、data type）和设备位置对于 debugging 和确保操作之间的兼容性至关重要。

.. code-block:: python

    >>> x = torch.randn(2, 3, 4)
    >>> x.shape
    torch.Size([2, 3, 4])
    >>> x.size()
    torch.Size([2, 3, 4])
    >>> x.dtype
    torch.float32
    >>> x.device
    device(type='cpu')
    >>> x.numel()
    24

连续张量（Contiguous Tensors）
------------------------------------------------

对于某些操作，Tensors 必须存储在连续的内存块中。经过 ``transpose`` 或 ``permute`` 等操作后，tensors 可能不连续。需要时使用 ``contiguous()`` 创建连续副本。

.. code-block:: python

    >>> x = torch.randn(2, 3)
    >>> x.is_contiguous()
    True
    >>> y = x.transpose(0, 1)
    >>> y.is_contiguous()
    False
    >>> z = y.contiguous()
    >>> z.is_contiguous()
    True

视图与重塑（View vs Reshape）
--------------------------------------------

``view()`` 要求 tensors 是连续的，并返回共享相同内存的视图。 ``reshape()`` 适用于连续和非连续的 tensors，并根据需要创建副本。当您知道 tensor 是连续的时，请使用 ``view()`` 以获得更好的性能。

.. code-block:: python

    >>> x = torch.randn(2, 3, 4)
    >>> x.is_contiguous()
    True
    >>> x.view(2, 12).shape
    torch.Size([2, 12])

    >>> y = x.transpose(0, 1)
    >>> y.is_contiguous()
    False
    >>> y.view(3, 8)
    RuntimeError: view size is not compatible with input tensor's size and stride

    >>> y.reshape(3, 8).shape
    torch.Size([3, 8])
    >>> y.contiguous().view(3, 8).shape
    torch.Size([3, 8])

重塑张量（Reshape Tensors）
------------------------------------------

用于为神经网络层准备数据的常见重塑操作。

.. code-block:: python

    x = torch.randn(2, 3, 4)
    x.reshape(6, 4)
    x.flatten()
    x.squeeze()
    x.unsqueeze(0)

移动张量（Move Tensors）
------------------------------------

在CPU和GPU之间，或在不同的GPU设备之间传输tensors。在不同设备上处理模型和数据时，这是必要的。

.. code-block:: python

    x = torch.randn(2, 3)
    x_gpu = x.to('cuda')
    x_gpu = x.cuda()
    x_cpu = x_gpu.to('cpu')
    x_cpu = x_gpu.cpu()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    x = x.to(device)

算术（Arithmetic）
----------------------------

PyTorch支持element明智的运算和矩阵运算。大多数操作都有函数式和method两种形式，并且支持broadcasting到tensors不同的shapes。

.. code-block:: python

    >>> x = torch.rand(2, 2, device=0)
    >>> y = torch.rand(2, 2, device=0)
    >>> x
    tensor([[0.2171, 0.7797],
            [0.7265, 0.6759]], device='cuda:0')
    >>> y
    tensor([[0.6766, 0.1862],
            [0.2438, 0.0076]], device='cuda:0')

    >>> x + y
    tensor([[0.8937, 0.9659],
            [0.9703, 0.6834]], device='cuda:0')
    >>> torch.add(x, y)
    tensor([[0.8937, 0.9659],
            [0.9703, 0.6834]], device='cuda:0')
    >>> x - y
    tensor([[-0.4594,  0.5935],
            [ 0.4827,  0.6683]], device='cuda:0')
    >>> x * y
    tensor([[0.1469, 0.1452],
            [0.1771, 0.0051]], device='cuda:0')
    >>> x / y
    tensor([[ 0.3209,  4.1880],
            [ 2.9796, 89.4011]], device='cuda:0')
    >>> x ** 2
    tensor([[0.0471, 0.6079],
            [0.5278, 0.4568]], device='cuda:0')
    >>> x @ y
    tensor([[0.3370, 0.0463],
            [0.6563, 0.1404]], device='cuda:0')
    >>> torch.matmul(x, y)
    tensor([[0.3370, 0.0463],
            [0.6563, 0.1404]], device='cuda:0')

原地操作（In-place Operations）
--------------------------------------------------

以 ``_`` 结尾的操作直接修改tensors，无需创建新的tensors，节省内存。小心使用它们，因为它们会影响梯度计算。

.. code-block:: python

    x = torch.rand(2, 2, device=0)
    y = torch.rand(2, 2, device=0)
    y.add_(x)
    y.sub_(x)
    y.mul_(x)
    y.div_(x)
    y.zero_()
    y.fill_(5)

转置（Transpose）
--------------------------

交换多维tensors的维度。当为需要特定输入 shapes 的不同神经网络层准备数据时，通常会使用此方法。

.. code-block:: python

    >>> x = torch.randn(2, 6, 2, device=0)
    >>> x.shape
    torch.Size([2, 6, 2])
    >>> y = x.transpose(1, 2)
    >>> y.shape
    torch.Size([2, 2, 6])
    >>> x.T.shape
    torch.Size([2, 2, 6])
    >>> x.permute(2, 0, 1).shape
    torch.Size([2, 2, 6])

矩阵乘法（Matrix Multiplication）
------------------------------------------------------

对高维 tensors 执行批量矩阵运算。这是神经网络计算的基础，您可以同时进行多个样本 process。

.. code-block:: python

    >>> x = torch.randn(1, 2, 3, 4, device=0)
    >>> x @ x.transpose(2, 3)
    tensor([[[[ 1.0950, -0.1160, -1.4840],
              [-0.1160,  2.4025,  2.8093],
              [-1.4840,  2.8093,  5.9335]],

             [[ 3.2498, -0.3049, -0.5129],
              [-0.3049,  0.1591, -0.2596],
              [-0.5129, -0.2596,  2.9863]]]], device='cuda:0')

    >>> torch.bmm(x, x.transpose(2, 3))
    >>> torch.einsum('bijk,bikl->bijl', x, x.transpose(2, 3))

聚合（Aggregation）
------------------------------

使用聚合 functions 沿指定维度减少 tensors。这些操作对于计算统计数据和降维至关重要。

.. code-block:: python

    >>> x = torch.randn(2, 3, 4)
    >>> x.sum()
    tensor(5.2341)
    >>> x.sum(dim=0).shape
    torch.Size([3, 4])
    >>> x.sum(dim=-1).shape
    torch.Size([2, 3])
    >>> x.mean()
    tensor(0.2181)
    >>> x.std()
    tensor(1.0234)
    >>> x.max()
    tensor(2.3456)
    >>> x.min()
    tensor(-1.8765)
    >>> x.argmax()
    tensor(7)
    >>> x.argmin()
    tensor(15)

    >>> x.max(dim=1)
    torch.return_types.max(
    values=tensor([[1.2345, 0.9876, 1.5432, 0.8765],
                   [0.7654, 1.3456, 0.6543, 1.2345]]),
    indices=tensor([[1, 2, 0, 1],
                    [2, 0, 1, 2]]))

切片（Slicing）
----------------------

使用 NumPy 样式索引提取 tensors 的部分内容。切片对于在不复制数据的情况下访问特定的 elements、行、列或子 tensors 至关重要。

.. code-block:: python

    >>> x = torch.randn(2, 3, device=0)
    >>> x
    tensor([[-1.3921,  0.0475,  0.7571],
            [-0.1469, -0.3882,  0.2149]], device='cuda:0')
    >>> x[:, 1]
    tensor([ 0.0475, -0.3882], device='cuda:0')
    >>> x[1, :]
    tensor([-0.1469, -0.3882,  0.2149], device='cuda:0')
    >>> x[1, 1].item()
    -0.3882044851779938

    >>> x = torch.triu(torch.ones(5, 5))
    >>> x[:3, :3]
    tensor([[1., 1., 1.],
            [0., 1., 1.],
            [0., 0., 1.]])

高级索引（Advanced Indexing）
----------------------------------------------

使用 boolean 掩码和花式索引根据条件或特定 index arrays 选择 elements。

.. code-block:: python

    >>> x = torch.randn(3, 4)
    >>> mask = x > 0
    >>> x[mask]
    tensor([0.5234, 1.2345, 0.8765, 0.3456, 1.5678])

    x[x > 0] = 0

    indices = torch.tensor([0, 2])
    x[indices]
    x[[0, 1], [1, 2]]

拼接（Concatenation）
----------------------------------

沿现有或新尺寸组合多个 tensors。这对于构建批次或组合来自不同来源的功能非常有用。

.. code-block:: python

    >>> x = torch.randn(2, 3)
    >>> y = torch.randn(2, 3)
    >>> torch.cat([x, y], dim=0).shape
    torch.Size([4, 3])
    >>> torch.cat([x, y], dim=1).shape
    torch.Size([2, 6])
    >>> torch.stack([x, y], dim=0).shape
    torch.Size([2, 2, 3])
    >>> torch.vstack([x, y]).shape
    torch.Size([4, 3])
    >>> torch.hstack([x, y]).shape
    torch.Size([2, 6])

拆分（Splitting）
--------------------------

将 tensors 拆分为多个块或沿特定维度。对于跨多个 GPU 分发数据或小批量处理非常有用。

.. code-block:: python

    >>> x = torch.randn(6, 4)
    >>> chunks = torch.split(x, 2, dim=0)
    >>> len(chunks)
    3
    >>> chunks = torch.chunk(x, 3, dim=0)
    >>> len(chunks)
    3
    >>> tensors = x.unbind(dim=0)
    >>> len(tensors)
    6

梯度（Gradient）
------------------------

自动微分是PyTorch训练神经网络的核心功能。在 tensors 上启用梯度跟踪以在反向传播期间计算导数。

.. code-block:: python

    >>> x = torch.randn(3, requires_grad=True, device=0)
    >>> x
    tensor([-1.1442, -0.8709, -0.2581], device='cuda:0', requires_grad=True)

    >>> y = x.detach()
    >>> y
    tensor([-1.1442, -0.8709, -0.2581], device='cuda:0')

    >>> x.requires_grad_(False)
    tensor([-1.1442, -0.8709, -0.2581], device='cuda:0')

禁用梯度（Disable Gradient）
--------------------------------------------

暂时禁用梯度计算以进行推理或不需要梯度时。这减少了内存使用并加快了计算速度。

.. code-block:: python

    >>> x = torch.randn(3, requires_grad=True, device=0)
    >>> with torch.no_grad():
    ...     y = x + 1
    ...     print(y)
    ...
    tensor([1.2969, 1.5251, 0.7915], device='cuda:0')

    with torch.inference_mode():
        y = x * 2

    @torch.no_grad()
    def predict(x):
        return model(x)

反向传播（Backpropagation）
------------------------------------------

使用自动微分计算梯度。 PyTorch 在前向传递过程中构建计算图，并在后向传递过程中使用链式法则计算梯度。

.. code-block:: python

    >>> x = torch.randn(3, requires_grad=True)
    >>> y = x + 1
    >>> z = y * y * 3
    >>> z = z.mean()
    >>> z.backward()
    >>> x.grad
    tensor([1.2036, 5.0103, 0.5143])

    x.grad.zero_()
    z.backward()

梯度累积（Gradient Accumulation）
------------------------------------------------------

在多次向后传递中累积梯度。当 GPU 内存有限时，这对于模拟较大的批量大小非常有用。

.. code-block:: python

    optimizer.zero_grad()
    for i, (inputs, targets) in enumerate(dataloader):
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        if (i + 1) % accumulation_steps == 0:
            optimizer.step()
            optimizer.zero_grad()

神经网络模块（Neural Network Module）
----------------------------------------------------------

通过子类化 ``nn.Module`` 来定义神经网络。这为构建具有自动 parameter 管理的 complex 模型提供了一个干净的界面。

.. code-block:: python

    import torch.nn as nn

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(784, 128)
            self.fc2 = nn.Linear(128, 10)

        def forward(self, x):
            x = torch.relu(self.fc1(x))
            x = self.fc2(x)
            return x

    model = Net()
    model.to('cuda')

常用网络层（Common Layers）
----------------------------------------

PyTorch 提供了多种用于构建神经网络的预构建层。

.. code-block:: python

    import torch.nn as nn

    linear = nn.Linear(10, 5)
    conv2d = nn.Conv2d(3, 64, kernel_size=3, padding=1)
    maxpool = nn.MaxPool2d(2, 2)
    dropout = nn.Dropout(0.5)
    batchnorm = nn.BatchNorm2d(64)
    relu = nn.ReLU()
    sigmoid = nn.Sigmoid()
    softmax = nn.Softmax(dim=1)

    lstm = nn.LSTM(input_size=10, hidden_size=20, num_layers=2)
    gru = nn.GRU(input_size=10, hidden_size=20)
    embedding = nn.Embedding(1000, 128)

损失函数（Loss Functions）
----------------------------------------

损失 functions 衡量模型的预测与目标 values 的匹配程度。根据您的任务选择合适的损失 function。

.. code-block:: python

    import torch.nn as nn

    mse_loss = nn.MSELoss()
    cross_entropy = nn.CrossEntropyLoss()
    bce_loss = nn.BCELoss()
    bce_with_logits = nn.BCEWithLogitsLoss()
    l1_loss = nn.L1Loss()
    nll_loss = nn.NLLLoss()

    outputs = model(inputs)
    loss = cross_entropy(outputs, targets)

优化器（Optimizers）
------------------------------

优化器根据计算的梯度更新模型 parameters。不同的优化器对 parameter 更新使用不同的策略。

.. code-block:: python

    import torch.optim as optim

    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    optimizer = optim.RMSprop(model.parameters(), lr=0.01)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

学习率调度器（Learning Rate Scheduler）
--------------------------------------------------------------

在训练过程中调整学习率以提高收敛性和模型性能。

.. code-block:: python

    from torch.optim.lr_scheduler import StepLR, ReduceLROnPlateau

    scheduler = StepLR(optimizer, step_size=30, gamma=0.1)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', patience=10)

    for epoch in range(num_epochs):
        train(...)
        val_loss = validate(...)
        scheduler.step(val_loss)

训练循环（Training Loop）
--------------------------------------

典型的训练 loop 涉及前向传递、损失计算、后向传递和 parameter 更新。

.. code-block:: python

    model.train()
    for epoch in range(num_epochs):
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            print(f'Loss: {loss.item():.4f}')

评估模式（Evaluation Mode）
------------------------------------------

在训练和评估模式之间切换以控制层的行为，例如 dropout 和批量归一化。

.. code-block:: python

    model.eval()
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            predictions = outputs.argmax(dim=1)

保存和加载模型（Save and Load Models）
----------------------------------------------------------

将经过训练的模型保存到磁盘并稍后加载以进行推理或继续训练。

.. code-block:: python

    torch.save(model.state_dict(), 'model.pth')
    model.load_state_dict(torch.load('model.pth'))

    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }, 'checkpoint.pth')

    checkpoint = torch.load('checkpoint.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

DataLoader 数据加载（DataLoader）
------------------------------------------------------

高效加载和批量训练数据。 DataLoader 处理洗牌、批处理和并行数据加载。

.. code-block:: python

    from torch.utils.data import DataLoader, TensorDataset

    dataset = TensorDataset(x_train, y_train)
    loader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4)

    for batch_x, batch_y in loader:
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)

自定义数据集（Custom Dataset）
--------------------------------------------

通过子类化 ``Dataset`` 来创建自定义数据集，以从各种源加载数据。

.. code-block:: python

    from torch.utils.data import Dataset

    class CustomDataset(Dataset):
        def __init__(self, data, labels):
            self.data = data
            self.labels = labels

        def __len__(self):
            return len(self.data)

        def __getitem__(self, idx):
            return self.data[idx], self.labels[idx]

    dataset = CustomDataset(x_train, y_train)
    loader = DataLoader(dataset, batch_size=32)

NumPy 转换（NumPy Conversion）
----------------------------------------------------

在 PyTorch tensors 和 NumPy arrays 之间进行转换，以实现与其他 libraries 的互操作性。请注意，GPU 上的 tensors 必须先移至 CPU。

.. code-block:: python

    >>> x = torch.randn([1, 2, 3], device=0)
    >>> y = x.cpu().numpy()
    >>> y
    array([[[-0.11979043,  0.13762406, -1.2633433 ],
            [-0.380241  ,  1.5320604 , -1.0828359 ]]], dtype=float32)

    import numpy as np
    arr = np.array([[1, 2], [3, 4]])
    tensor = torch.from_numpy(arr)

共享内存（Shared Memory）
--------------------------------------

CPU tensors 和 NumPy arrays 可以共享相同的底层内存，因此对其中一个的修改会影响另一个。

.. code-block:: python

    >>> x = torch.randn(1, 2, 3)
    >>> y = x.numpy()
    >>> x.add_(1)
    tensor([[[ 1.8195,  3.0259,  0.6733],
             [ 2.6539,  1.1562, -0.9821]]])
    >>> y
    array([[[ 1.8194908 ,  3.0258512 ,  0.67326605],
            [ 2.6539469 ,  1.1561831 , -0.98211455]]], dtype=float32)

随机种子（Random Seed）
----------------------------------

Set 随机种子，用于不同运行之间的再现性。这可以确保 debugging 或比较实验时得到一致的结果。

.. code-block:: python

    torch.manual_seed(42)
    torch.cuda.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    import numpy as np
    import random
    np.random.seed(42)
    random.seed(42)

GPU 内存管理（GPU Memory Management）
--------------------------------------------------------------

监控和管理 GPU 内存使用情况，以避免内存不足错误并优化性能。

.. code-block:: python

    >>> torch.cuda.empty_cache()
    >>> torch.cuda.memory_allocated()
    1073741824
    >>> torch.cuda.memory_reserved()
    2147483648
    >>> torch.cuda.max_memory_allocated()
    3221225472

    torch.cuda.reset_peak_memory_stats()
    print(torch.cuda.memory_summary())


分布式训练（Distributed Training）
------------------------------------------------------

NCCL（NVIDIA集体通信Library）可实现高效的多GPU和多节点训练。初始化分布式process组并检查其状态。

.. code-block:: python

    >>> import torch.distributed as dist
    >>> dist.is_available()
    True
    >>> dist.is_nccl_available()
    True
    >>> dist.is_initialized()
    False

    dist.init_process_group(backend='nccl')

    >>> dist.is_initialized()
    True
    >>> dist.get_rank()
    0
    >>> dist.get_world_size()
    4
    >>> dist.get_backend()
    'nccl'

使用 torchrun 启动（Launch with torchrun）
------------------------------------------------------------------------

使用 ``torchrun`` 跨多个 GPU 或节点启动分布式训练。它自动将sets搭建环境variables进行分布式训练。

.. code-block:: bash

    # 单节点、多GPU
    torchrun --nproc_per_node=4 train.py

    # 多个节点
    torchrun --nproc_per_node=4 \
             --nnodes=2 \
             --node_rank=0 \
             --master_addr="192.168.1.1" \
             --master_port=29500 \
             train.py

使用 Slurm 启动（Launch with Slurm）
------------------------------------------------------------

向Slurm集群提交分布式训练作业。 Slurm 管理资源分配和节点分配。有关更多 Slurm 示例，请参阅 :doc:`../hpc/slurm` 。

.. code-block:: bash

    #!/bin/bash
    #SBATCH --job-name=pytorch_ddp
    #SBATCH --nodes=2
    #SBATCH --ntasks-per-node=4
    #SBATCH --gres=gpu:4
    #SBATCH --time=24:00:00

    export MASTER_ADDR=$(scontrol show hostname $SLURM_NODELIST | head -n 1)
    export MASTER_PORT=29500

    srun torchrun --nproc_per_node=4 \
                  --nnodes=$SLURM_NNODES \
                  --node_rank=$SLURM_NODEID \
                  --master_addr=$MASTER_ADDR \
                  --master_port=$MASTER_PORT \
                  train.py

DistributedDataParallel 分布式训练（DistributedDataParallel）
------------------------------------------------------------------------------------------------------------

用 DDP 包裹您的模型以进行多 GPU 训练。 DDP 使用 NCCL 实现跨 GPU 的高效梯度同步。

.. code-block:: python

    import torch.nn as nn
    from torch.nn.parallel import DistributedDataParallel as DDP

    model = Net().to(device)
    model = DDP(model, device_ids=[local_rank])

    for inputs, targets in train_loader:
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

集合通信操作（Collective Operations）
----------------------------------------------------------

NCCL为分布式训练提供集体通信操作。

.. code-block:: python

    import torch.distributed as dist

    tensor = torch.randn(2, 3).cuda()

    dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
    dist.broadcast(tensor, src=0)
    dist.all_gather(tensor_list, tensor)
    dist.reduce(tensor, dst=0, op=dist.ReduceOp.SUM)
    dist.barrier()
