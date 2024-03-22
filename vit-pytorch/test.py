import torch
from vit_pytorch import ViT
def test():
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

if __name__ == "__main__":
    test()