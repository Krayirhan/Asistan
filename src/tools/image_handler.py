from __future__ import annotations

"""
Image Handler - Görsel işleme araçları
Resim yükleme, boyutlandırma, format dönüşümü
"""

import os
from typing import Optional, Tuple
from pathlib import Path
from loguru import logger

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow yüklü değil! pip install Pillow")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV yüklü değil")


class ImageHandler:
    """Görsel işleme araçları"""
    
    def __init__(self, config: dict):
        self.config = config.get('vlm', {})
        self.target_size = tuple(self.config.get('image_resize', [384, 384]))
        
    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """
        Resmi yükle
        
        Args:
            image_path: Resim dosya yolu
        
        Returns:
            PIL Image veya None
        """
        
        if not PIL_AVAILABLE:
            logger.error("Pillow yüklü değil!")
            return None
        
        if not os.path.exists(image_path):
            logger.error(f"Resim bulunamadı: {image_path}")
            return None
        
        try:
            image = Image.open(image_path)
            logger.success(f"Resim yüklendi: {image_path} ({image.size})")
            return image
            
        except Exception as e:
            logger.error(f"Resim yükleme hatası: {e}")
            return None
    
    def resize_image(
        self,
        image: Image.Image,
        size: Optional[Tuple[int, int]] = None,
        maintain_aspect: bool = True
    ) -> Image.Image:
        """
        Resmi yeniden boyutlandır
        
        Args:
            image: PIL Image
            size: Hedef boyut (width, height)
            maintain_aspect: En-boy oranını koru
        
        Returns:
            Yeniden boyutlandırılmış resim
        """
        
        if not PIL_AVAILABLE:
            raise RuntimeError("Pillow yüklü değil")

        size = size or self.target_size
        
        if maintain_aspect:
            # En-boy oranını koruyarak resize
            image.thumbnail(size, Image.Resampling.LANCZOS)
        else:
            # Tam boyuta resize
            image = image.resize(size, Image.Resampling.LANCZOS)
        
        logger.debug(f"Resim yeniden boyutlandırıldı: {image.size}")
        return image
    
    def convert_to_rgb(self, image: Image.Image) -> Image.Image:
        """
        Resmi RGB'ye çevir
        
        Args:
            image: PIL Image
        
        Returns:
            RGB formatta resim
        """
        
        if not PIL_AVAILABLE:
            raise RuntimeError("Pillow yüklü değil")

        if image.mode != 'RGB':
            image = image.convert('RGB')
            logger.debug("Resim RGB'ye çevrildi")
        
        return image
    
    def optimize_for_vlm(self, image_path: str, output_path: Optional[str] = None) -> str:
        """
        Resmi VLM için optimize et (boyutlandır, format dönüşümü)
        
        Args:
            image_path: Kaynak resim yolu
            output_path: Çıktı yolu (None = geçici dosya)
        
        Returns:
            Optimize edilmiş resim yolu
        """
        
        image = self.load_image(image_path)
        if not image:
            return image_path
        
        # RGB'ye çevir
        image = self.convert_to_rgb(image)
        
        # Yeniden boyutlandır
        image = self.resize_image(image)
        
        # Kaydet
        if output_path is None:
            output_path = f"cache/temp_{Path(image_path).stem}_optimized.jpg"
            os.makedirs("cache", exist_ok=True)
        
        try:
            image.save(output_path, format='JPEG', quality=90)
            logger.success(f"Optimize edilmiş resim: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Resim kaydetme hatası: {e}")
            return image_path
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Resim hakkında bilgi al
        
        Args:
            image_path: Resim yolu
        
        Returns:
            Bilgi dict'i
        """
        
        image = self.load_image(image_path)
        if not image:
            return {}
        
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        
        return {
            'path': image_path,
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'file_size_mb': round(file_size_mb, 2)
        }
    
    def apply_blur(self, image: Image.Image, radius: int = 5) -> Image.Image:
        """
        Resme blur uygula (opsiyonel - preview için)
        
        Args:
            image: PIL Image
            radius: Blur yarıçapı
        
        Returns:
            Blur uygulanmış resim
        """
        
        if not PIL_AVAILABLE:
            raise RuntimeError("Pillow yüklü değil")

        from PIL import ImageFilter
        return image.filter(ImageFilter.GaussianBlur(radius=radius))
    
    @staticmethod
    def is_valid_image(file_path: str) -> bool:
        """
        Dosya geçerli bir resim mi?
        
        Args:
            file_path: Dosya yolu
        
        Returns:
            Geçerli mi?
        """
        
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        ext = Path(file_path).suffix.lower()
        
        return ext in valid_extensions and os.path.exists(file_path)
