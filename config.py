import google.generativeai as genai
import torch

def configurar_ambiente():
    genai.configure(api_key="TOKEN DE GOOGLE AI")
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
