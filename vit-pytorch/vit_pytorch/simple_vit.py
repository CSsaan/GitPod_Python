import torch
from torch import nn

from einops import rearrange
from einops.layers.torch import Rearrange

# helpers

def pair(t):
    return t if isinstance(t, tuple) else (t, t)

def posemb_sincos_2d(h, w, dim, temperature: int = 10000, dtype = torch.float32):
    y, x = torch.meshgrid(torch.arange(h), torch.arange(w), indexing="ij") # [8*8]个位置、[8*8]个位置
    assert (dim % 4) == 0, "feature dimension must be multiple of 4 for sincos emb"
    omega = torch.arange(dim // 4) / (dim // 4 - 1) # 大小变为1/4
    omega = 1.0 / (temperature ** omega)

    y = y.flatten()[:, None] * omega[None, :] # [64,1] * [1,256] -> [64, 256]
    x = x.flatten()[:, None] * omega[None, :]
    pe = torch.cat((x.sin(), x.cos(), y.sin(), y.cos()), dim=1) # 再拼接回4倍
    return pe.type(dtype)

# classes

class FeedForward(nn.Module):
    def __init__(self, dim, hidden_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, dim),
        )
    def forward(self, x):
        return self.net(x)

class Attention(nn.Module):
    def __init__(self, dim, heads = 8, dim_head = 64):
        super().__init__()
        inner_dim = dim_head *  heads
        self.heads = heads
        self.scale = dim_head ** -0.5
        self.norm = nn.LayerNorm(dim)

        self.attend = nn.Softmax(dim = -1)

        self.to_qkv = nn.Linear(dim, inner_dim * 3, bias = False)
        self.to_out = nn.Linear(inner_dim, dim, bias = False)

    def forward(self, x):
        x = self.norm(x)

        qkv = self.to_qkv(x).chunk(3, dim = -1)
        q, k, v = map(lambda t: rearrange(t, 'b n (h d) -> b h n d', h = self.heads), qkv)

        dots = torch.matmul(q, k.transpose(-1, -2)) * self.scale

        attn = self.attend(dots)

        out = torch.matmul(attn, v)
        out = rearrange(out, 'b h n d -> b n (h d)')
        return self.to_out(out)

class Transformer(nn.Module):
    def __init__(self, dim, depth, heads, dim_head, mlp_dim):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(nn.ModuleList([
                Attention(dim, heads = heads, dim_head = dim_head),
                FeedForward(dim, mlp_dim)
            ]))
    def forward(self, x):
        for attn, ff in self.layers:
            x = attn(x) + x
            x = ff(x) + x
        return self.norm(x)

class SimpleViT(nn.Module):
    def __init__(self, *, image_size, patch_size, num_classes, dim, depth, heads, mlp_dim, channels = 3, dim_head = 64):
        """
        《Vision Transformer》原始论文的部分作者提出了一项更新，提出了简化`ViT`的方法，使其能够更快速、更好地训练。
        这些简化包括使用2D正弦位置嵌入、全局平均池化（无CLS标记）、无dropout、批量大小从4096减少到1024，并使用RandAugment和MixUp数据增强。
        他们还表明，简单的线性层结尾并不明显比原始的MLP头差。
        您可以通过导入以下方式使用`SimpleViT`。

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
        """
        super().__init__()
        image_height, image_width = pair(image_size)
        patch_height, patch_width = pair(patch_size)

        assert image_height % patch_height == 0 and image_width % patch_width == 0, 'Image dimensions must be divisible by the patch size.'

        patch_dim = channels * patch_height * patch_width

        self.to_patch_embedding = nn.Sequential(
            Rearrange("b c (h p1) (w p2) -> b (h w) (p1 p2 c)", p1 = patch_height, p2 = patch_width), # [1, 3, (h*32) (w*32)] -> [1batch, (8*8)个, (32*32*3)patch像素]
            nn.LayerNorm(patch_dim),
            nn.Linear(patch_dim, dim), # [1, 64, 32*32*3] -> [1batch, 64个patch, 1024]
            nn.LayerNorm(dim),
        )

        self.pos_embedding = posemb_sincos_2d(
            h = image_height // patch_height,
            w = image_width // patch_width,
            dim = dim,
        ) 

        self.transformer = Transformer(dim, depth, heads, dim_head, mlp_dim)

        self.pool = "mean"
        self.to_latent = nn.Identity()

        self.linear_head = nn.Linear(dim, num_classes)

    def forward(self, img):
        device = img.device

        x = self.to_patch_embedding(img)
        x += self.pos_embedding.to(device, dtype=x.dtype)
        x = self.transformer(x)
        x = x.mean(dim = 1)

        x = self.to_latent(x)
        return self.linear_head(x)
