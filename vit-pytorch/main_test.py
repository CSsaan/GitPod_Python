import torch
from vit_pytorch import *
from vit_pytorch.na_vit import NaViT
from torchvision.models import resnet50
from vit_pytorch.distill import DistillableViT, DistillWrapper

# ---------------------------- 1 ----------------------------
def run_ViT():
    v = ViT(
        image_size = 256,
        patch_size = 32,
        num_classes = 1000,
        dim = 1024,
        depth = 6,
        heads = 16,
        mlp_dim = 2048,
        pool = 'mean', # {'cls', 'mean'}
        dropout = 0.1,
        emb_dropout = 0.1
    )

    batch_size = 1
    img = torch.randn(batch_size, 3, 256, 256) # b c h w

    preds = v(img)
    print("result: ", preds.shape)
    assert preds.shape == (batch_size, 1000), 'correct logits outputted'

# ---------------------------- 2 ----------------------------
def run_SimpleViT():
    v = SimpleViT(
        image_size = 256,
        patch_size = 32,
        num_classes = 1000,
        dim = 1024,
        depth = 6,
        heads = 16,
        mlp_dim = 2048
    )
    img = torch.randn(1, 3, 256, 256)
    preds = v(img) # (1, 1000)
    print("result: ", preds.shape)

# ---------------------------- 3 ----------------------------
def run_NaViT():
    v = NaViT(
        image_size = 256,
        patch_size = 32,
        num_classes = 1000,
        dim = 1024,
        depth = 6,
        heads = 16,
        mlp_dim = 2048,
        dropout = 0.1,
        emb_dropout = 0.1,
        token_dropout_prob = 0.1  # token dropout of 10% (keep 90% of tokens)
    )
    images = [
        [torch.randn(3, 256, 256), torch.randn(3, 128, 128)],
        [torch.randn(3, 128, 256), torch.randn(3, 256, 128)],
        [torch.randn(3, 64, 256)]
    ]
    preds = v(images) # (5, 1000)
    print("result: ", preds.shape)

# ---------------------------- 4 ----------------------------
def run_distill():
    teacher = resnet50(pretrained = True)
    v = DistillableViT(
    image_size = 256,
    patch_size = 32,
    num_classes = 1000,
    dim = 1024,
    depth = 6,
    heads = 8,
    mlp_dim = 2048,
    dropout = 0.1,
    emb_dropout = 0.1
    )
    distiller = DistillWrapper(
        student = v,
        teacher = teacher,
        temperature = 3,           # temperature of distillation
        alpha = 0.5,               # trade between main loss and distillation loss
        hard = False               # whether to use soft or hard distillation
    )

    img = torch.randn(2, 3, 256, 256)
    labels = torch.randint(0, 1000, (2,))

    loss = distiller(img, labels)
    loss.backward()

    # after lots of training above ...
    pred = v(img) # (2, 1000)
    print("result: ", pred.shape)

# ---------------------------- 5 ----------------------------


# ---------------------------- 6 ----------------------------


# ---------------------------- 7 ----------------------------


# ---------------------------- 8 ----------------------------

if __name__ == "__main__":
    # 选择调用模型
    case_number = 4 
    # 所有模型
    all_ViT_dict = {
        1: run_ViT,
        2: run_SimpleViT,
        3: run_NaViT,
        4: run_distill,
    }
    
    # 根据不同情况选择执行对应的函数
    all_ViT_dict.get(case_number, lambda: "Invalid case")()

  