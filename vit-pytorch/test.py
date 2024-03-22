import torch
from vit_pytorch import *

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


# ---------------------------- 4 ----------------------------


# ---------------------------- 5 ----------------------------


# ---------------------------- 6 ----------------------------


# ---------------------------- 7 ----------------------------


# ---------------------------- 8 ----------------------------

if __name__ == "__main__":
    # 选择调用模型
    case_number = 2 
    # 所有模型
    all_ViT_dict = {
        1: run_ViT,
        2: run_SimpleViT,
    }
    
    # 根据不同情况选择执行对应的函数
    all_ViT_dict.get(case_number, lambda: "Invalid case")()

  