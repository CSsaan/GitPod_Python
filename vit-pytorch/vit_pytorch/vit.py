import torch
from torch import nn

from einops import rearrange, repeat
from einops.layers.torch import Rearrange

# helpers

def pair(t):
    return t if isinstance(t, tuple) else (t, t)

# classes

class FeedForward(nn.Module):
    def __init__(self, dim, hidden_dim, dropout = 0.):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, dim),
            nn.Dropout(dropout)
        )

    def forward(self, x):
        return self.net(x)

class Attention(nn.Module):
    def __init__(self, dim, heads = 8, dim_head = 64, dropout = 0.):
        super().__init__()
        inner_dim = dim_head *  heads
        project_out = not (heads == 1 and dim_head == dim)

        self.heads = heads
        self.scale = dim_head ** -0.5

        self.norm = nn.LayerNorm(dim)

        self.attend = nn.Softmax(dim = -1)
        self.dropout = nn.Dropout(dropout)

        self.to_qkv = nn.Linear(dim, inner_dim * 3, bias = False)

        self.to_out = nn.Sequential(
            nn.Linear(inner_dim, dim),
            nn.Dropout(dropout)
        ) if project_out else nn.Identity()

    def forward(self, x):
        x = self.norm(x)

        qkv = self.to_qkv(x).chunk(3, dim = -1)
        q, k, v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h = self.heads), qkv)

        dots = torch.matmul(q, k.transpose(-1, -2)) * self.scale

        attn = self.attend(dots)
        attn = self.dropout(attn)

        out = torch.matmul(attn, v)
        out = rearrange(out, 'b h n d -> b n (h d)')
        return self.to_out(out)

class Transformer(nn.Module):
    def __init__(self, dim, depth, heads, dim_head, mlp_dim, dropout = 0.):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(nn.ModuleList([
                Attention(dim, heads = heads, dim_head = dim_head, dropout = dropout),
                FeedForward(dim, mlp_dim, dropout = dropout)
            ]))

    def forward(self, x):
        for attn, ff in self.layers:
            x = attn(x) + x
            x = ff(x) + x

        return self.norm(x)

class ViT(nn.Module):
    def __init__(self, *, image_size, patch_size, num_classes, dim, depth, heads, mlp_dim, pool = 'cls', channels = 3, dim_head = 64, dropout = 0., emb_dropout = 0.):
        """
        实现了《Vision Transformer》的PyTorch版本，这是一种仅使用单个Transformer编码器就能在视觉分类任务中达到SOTA的简单方法。在Yannic Kilcher的视频中进一步解释了其重要性。
        这里实际上没有太多的代码，但为了让大家更快了解这场注意力革命，还是将其展示出来。
        关于带有预训练模型的PyTorch实现，请查看Ross Wightman的仓库[这里](https://github.com/rwightman/pytorch-image-models)。
        官方的Jax仓库在[这里](https://github.com/google-research/vision_transformer)。
        还有一个TensorFlow 2的翻译版本[这里](https://github.com/taki0112/vit-tensorflow)，由研究科学家Junho Kim创建！🙏
        由Enrico Shippole进行的Flax翻译在[这里](https://github.com/conceptofmind/vit-flax)！

        Args:
            `image_size`: int.  
                Image size. If you have rectangular images, make sure your image size is the maximum of the width and height
            `patch_size`: int.  
                Size of patches. `image_size` must be divisible by `patch_size`.  
                The number of patches is: ` n = (image_size // patch_size) ** 2` and `n` **must be greater than 16**.
            `num_classes`: int.  
                Number of classes to classify.
            `dim`: int.  
                Last dimension of output tensor after linear transformation `nn.Linear(..., dim)`.
            `depth`: int.  
                Number of Transformer blocks.
            `heads`: int.  
                Number of heads in Multi-head Attention layer. 
            `mlp_dim`: int.  
                Dimension of the MLP (FeedForward) layer. 
            `channels`: int, default `3`.  
                Number of image's channels. 
            `dim_head`: int. 
                Number of dim's head. 
            `dropout`: float between `[0, 1]`, default `0.`.  
                Dropout rate. 
            `emb_dropout`: float between `[0, 1]`, default `0`.  
                Embedding dropout rate.
            `pool`: string, either `cls` token pooling or `mean` pooling            
		"""
        super().__init__()
        # 正方形的image、patch块
        image_height, image_width = pair(image_size)
        patch_height, patch_width = pair(patch_size)
        # image的宽高可以整除patch宽高（正好分割成多个patch）
        assert image_height % patch_height == 0 and image_width % patch_width == 0, 'Image dimensions must be divisible by the patch size.'
        # patch数量
        num_patches = (image_height // patch_height) * (image_width // patch_width)
        patch_dim = channels * patch_height * patch_width
        assert pool in {'cls', 'mean'}, 'pool type must be either cls (cls token) or mean (mean pooling)'

        self.to_patch_embedding = nn.Sequential(
            # [1, 3, 256, 256]
            Rearrange('b c (h p1) (w p2) -> b (h w) (p1 p2 c)', p1 = patch_height, p2 = patch_width), # [1, 3, (8*32) (8*32)] -> [1batch, (8*8)个, (32*32*3)patch像素]
            nn.LayerNorm(patch_dim),
            nn.Linear(patch_dim, dim), # [1, 64, (32*32*3)] -> [1, 64, 1024]
            nn.LayerNorm(dim),
            # [1, 64, 1024]
        )

        self.pos_embedding = nn.Parameter(torch.randn(1, num_patches + 1, dim)) #  # [1, 64+1, 1024]
        self.cls_token = nn.Parameter(torch.randn(1, 1, dim)) # [1, 1, 1024]
        self.dropout = nn.Dropout(emb_dropout)

        self.transformer = Transformer(dim, depth, heads, dim_head, mlp_dim, dropout)

        self.pool = pool
        self.to_latent = nn.Identity()

        self.mlp_head = nn.Linear(dim, num_classes)

    def forward(self, img):
        x = self.to_patch_embedding(img) # [1, 3, 256, 256] -> [1, 64, 1024] 3D图片转2D矩阵
        b, n, _ = x.shape

        cls_tokens = repeat(self.cls_token, '1 1 d -> b 1 d', b = b) # [1, 1, 1024] -> [1*b, 1, 1024]
        x = torch.cat((cls_tokens, x), dim=1) # [1, 65, 1024]
        x += self.pos_embedding[:, :(n + 1)]  # [1, 65, 1024]
        x = self.dropout(x)

        x = self.transformer(x) # [1, 65, 1024]
        x = x.mean(dim = 1) if self.pool == 'mean' else x[:, 0] # [1, 65, 1024] -> [1, 1024]

        x = self.to_latent(x)

        return self.mlp_head(x) # [1, 1024] -> [1, 1000]
