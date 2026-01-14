
import cv2
import numpy as np
from typing import Optional, Tuple, Union
import os
import logging

logger = logging.getLogger(__name__)

class ImageMatcher:
    """图片匹配工具"""
    
    @staticmethod
    def find_image(
        screenshot: Union[np.ndarray, str], 
        template_path: str, 
        threshold: float = 0.6
    ) -> Optional[Tuple[int, int]]:
        """
        在截图中寻找模板图片
        
        Args:
            screenshot: 截图 (numpy array 或 路径)
            template_path: 模板图片路径
            threshold: 匹配阈值 (0.0 ~ 1.0)
            
        Returns:
            (center_x, center_y) 匹配中心坐标，未找到返回 None
        """
        try:
            # 加载模板
            if not os.path.exists(template_path):
                logger.error(f"模板文件不存在: {template_path}")
                return None
                
            template = cv2.imread(template_path)
            if template is None:
                logger.error(f"无法加载模板图片: {template_path}")
                return None
            
            # 确保截图是 numpy array
            if isinstance(screenshot, str):
                if not os.path.exists(screenshot):
                    logger.error(f"截图文件不存在: {screenshot}")
                    return None
                img = cv2.imread(screenshot)
            else:
                img = screenshot
                
            # 转换颜色空间 (如果需要)
            # OpenCV 默认是 BGR，如果传入的是 PIL (RGB) 可能需要转换
            # 这里假设传入的 screenshot 已经是 cv2 兼容格式 (BGR or RGB consistent)
            # 为了稳健，如果维度不一样，可以尝试转换
            
            # 确保图像也是 3 通道 (去除 Alpha 通道如果存在)
            if len(img.shape) == 3 and img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            elif len(img.shape) == 3 and img.shape[2] == 3:
                pass # 假设是 BGR
                
            # 模板也处理一下Alpha
            if len(template.shape) == 3 and template.shape[2] == 4:
                template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
                
            # 获取尺寸
            th, tw = template.shape[:2]
            
            # 匹配
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 详细日志
            logger.info(f"图片匹配: 模板={os.path.basename(template_path)}, 相似度={max_val:.3f}, 阈值={threshold}")
            

            
            if max_val >= threshold:
                center_x = max_loc[0] + tw // 2
                center_y = max_loc[1] + th // 2
                logger.info(f"图片匹配成功: 坐标=({center_x}, {center_y})")
                return (center_x, center_y)
            else:
                logger.warning(f"图片匹配失败: 相似度{max_val:.3f} < 阈值{threshold}")
                return None
                
        except Exception as e:
            logger.error(f"图片匹配出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
