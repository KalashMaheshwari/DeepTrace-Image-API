import sys
import os
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms

# Add cloned AIDE repo to Python sys path
sys.path.append(os.path.join(os.path.dirname(__file__), "AIDE"))

try:
    from models.AIDE import AIDE
    from data.dct import DCT_base_Rec_Module
    aide_model_class = AIDE
except ImportError as e:
    print(f"ImportError: {e}")
    aide_model_class = None


class AIDEInferenceEngine:
    def __init__(self, checkpoint_path="weights/aide_checkpoint.pth", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Initializing AIDE (ICLR 2025) Engine on {self.device}...")

        # Standard preprocessing transforms for AIDE
        self.transform_before_test = transforms.Compose([
            transforms.ToTensor(),
        ])
        
        self.transform_train = transforms.Compose([
            transforms.Resize([256, 256]),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        try:
            self.dct = DCT_base_Rec_Module()
        except Exception as e:
            print(f"DCT load error: {e}")
            self.dct = None

        # Load weights
        if os.path.exists(checkpoint_path) and aide_model_class is not None:
            # Pass None for resnet_path and "" for convnext_path so it doesn't try to load external weights
            # It will initialize the structure, and then we overwrite it with our local checkpoint
            try:
                self.model = aide_model_class(resnet_path=None, convnext_path="").to(self.device)
            except Exception as e:
                # Fallback to None if "" fails in open_clip
                self.model = aide_model_class(resnet_path=None, convnext_path=None).to(self.device)
                
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            self.model.load_state_dict(checkpoint.get("model", checkpoint), strict=False)
            self.model.eval()
            print("AIDE Checkpoint Loaded Successfully!")
            self.is_loaded = True
        else:
            print(f"[Warning] AIDE weights not found or AIDE repo not imported correctly.")
            self.is_loaded = False

    def predict(self, pil_image: Image.Image):
        """Returns the raw tensor output directly from the model."""
        if not self.is_loaded:
            return "Model not loaded"
            
        if self.dct is None:
            return "DCT module not loaded"

        image = self.transform_before_test(pil_image)
        x_minmin, x_maxmax, x_minmin1, x_maxmax1 = self.dct(image)
        
        x_0 = self.transform_train(image)
        x_minmin = self.transform_train(x_minmin) 
        x_maxmax = self.transform_train(x_maxmax)
        x_minmin1 = self.transform_train(x_minmin1) 
        x_maxmax1 = self.transform_train(x_maxmax1)
        
        # Shape becomes [5, 3, 256, 256] -> unsqueeze to [1, 5, 3, 256, 256]
        img_tensor = torch.stack([x_minmin, x_maxmax, x_minmin1, x_maxmax1, x_0], dim=0)
        img_tensor = img_tensor.unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(img_tensor)
            print(f"\n[DEBUG] Raw Model Output Tensor: {output}")
            
        return output.tolist()
