"""OCR文字识别工具"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class OCRDetector:
    """OCR文字检测器（使用PaddleOCR）"""
    
    def __init__(self):
        """初始化OCR检测器（使用PaddleOCR）"""
        self.reader = None
        self._init_reader()

    def _parse_results(self, results) -> List[Tuple[List, str, float]]:
        """解析OCR结果，兼容不同版本的返回格式"""
        if not results:
            return []
            
        parsed_data = []
        
        # 检查是否为新版格式 (list of dicts)
        # 例如: [{'dt_polys': [array...], 'rec_text': 'Hello', 'rec_score': 0.99}, ...]
        if isinstance(results, list) and len(results) > 0 and isinstance(results[0], dict):
            # Check for parallel list format (PP-OCRv4 / Structure format)
            # e.g. [{'rec_texts': ['...'], 'rec_scores': [...], 'dt_polys': [...]}]
            if 'rec_texts' in results[0] and isinstance(results[0]['rec_texts'], list):
                # Parallel lists format
                for page in results:
                    texts = page.get('rec_texts', [])
                    scores = page.get('rec_scores', [])
                    boxes = page.get('dt_polys', []) if 'dt_polys' in page else page.get('rec_boxes', [])
                    
                    # Ensure all lists have the same length
                    min_len = min(len(texts), len(scores), len(boxes))
                    
                    for i in range(min_len):
                        text = texts[i]
                        confidence = float(scores[i])
                        poly = boxes[i]
                        
                        bbox = []
                        if hasattr(poly, 'tolist'):
                            bbox = poly.tolist()
                        else:
                            bbox = poly
                            
                        parsed_data.append((bbox, text, confidence))
                        
            else:
                # List of dicts format (one dict per line)
                # e.g. [{'rec_text': '...', ...}, {'rec_text': '...', ...}]
                for item in results:
                    text = item.get('rec_text', '')
                    confidence = float(item.get('rec_score', 0.0))
                    
                    bbox = []
                    if 'dt_polys' in item and len(item['dt_polys']) > 0:
                        poly = item['dt_polys'][0]
                        if hasattr(poly, 'tolist'):
                            bbox = poly.tolist()
                        else:
                            bbox = poly
                    
                    parsed_data.append((bbox, text, confidence))
                
        # 检查是否为旧版格式 (list of pages -> list of items -> [bbox, (text, conf)])
        elif isinstance(results, list) and len(results) > 0:
            # 尝试获取第一页
            page = results[0]
            # 如果page是列表且包含内容
            if isinstance(page, list) and len(page) > 0:
                # 检查项目结构
                item = page[0]
                # 匹配格式 [bbox, (text, conf)]
                if isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[1], (list, tuple)):
                    for entry in page:
                        bbox, (text, confidence) = entry
                        parsed_data.append((bbox, text, confidence))
            
        return parsed_data
    
    def _init_reader(self):
        """初始化PaddleOCR引擎"""
        try:
            logger.info("正在初始化PaddleOCR引擎...")
            from paddleocr import PaddleOCR
            self.reader = PaddleOCR(
                use_angle_cls=True,  # 使用方向分类器
                lang='ch',           # 中文
                ocr_version='PP-OCRv4', # 强制使用v4版本（默认通常是Mobile）
            )
            logger.info("PaddleOCR引擎初始化完成")
        except Exception as e:
            logger.error(f"PaddleOCR引擎初始化失败: {e}")
            self.reader = None
    
    def preprocess_image(self, image: np.ndarray, enhance: bool = True) -> np.ndarray:
        """预处理图像以提高OCR识别率
        
        Args:
            image: 输入图像
            enhance: 是否进行增强处理
            
        Returns:
            处理后的图像
        """
        if not enhance:
            return image
        
        try:
            # 1. 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # 2. 放大图像2倍（提高小文字识别率）
            scale = 2
            enlarged = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
            # 3. 增强对比度（CLAHE - 自适应直方图均衡化）
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(enlarged)
            
            # 4. 去噪
            denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10, templateWindowSize=7, searchWindowSize=21)
            
            # 5. 转换回BGR格式（PaddleOCR需要彩色图像）
            result = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
            
            return result
            
        except Exception as e:
            logger.warning(f"图像预处理失败: {e}，使用原始图像")
            return image
    
    def detect_text(self, image: np.ndarray, keywords: List[str], 
                   confidence_threshold: float = 0.5) -> List[Tuple[str, Tuple[int, int], float]]:
        """在图像中检测关键词
        
        Args:
            image: 输入图像（numpy数组）
            keywords: 要检测的关键词列表
            confidence_threshold: 置信度阈值
            
        Returns:
            检测结果列表，每项为 (匹配的文字, (中心x, 中心y), 置信度)
        """
        if self.reader is None:
            logger.error("OCR引擎未初始化")
            return []
        
        try:
            # 执行OCR识别
            # PaddleOCR 使用 .ocr() 方法，而不是 .readtext()
            # cls=True 启用方向分类
            results = self.reader.ocr(image)
            
            # 解析结果
            parsed_results = self._parse_results(results)
            
            matches = []
            for bbox, text, confidence in parsed_results:
                
                # 检查是否包含任何关键词
                for keyword in keywords:
                    if keyword in text and confidence >= confidence_threshold:
                        # 计算边界框中心点
                        bbox_array = np.array(bbox)
                        center_x = int(np.mean(bbox_array[:, 0]))
                        center_y = int(np.mean(bbox_array[:, 1]))
                        
                        matches.append((text, (center_x, center_y), confidence))
                        logger.info(f"检测到文字: '{text}' 位置: ({center_x}, {center_y}) 置信度: {confidence:.2f}")
                        break
            
            return matches
            
        except Exception as e:
            logger.error(f"OCR检测失败: {e}")
            return []
    
    def find_text(self, image: np.ndarray, target_text: str, 
                 fuzzy: bool = True, confidence_threshold: float = 0.5) -> Optional[Tuple[int, int]]:
        """查找特定文字的位置
        
        Args:
            image: 输入图像
            target_text: 目标文字
            fuzzy: 是否模糊匹配
            confidence_threshold: 置信度阈值
            
        Returns:
            文字中心坐标 (x, y)，未找到返回 None
        """
        if self.reader is None:
            logger.error("OCR引擎未初始化")
            return None
        
        try:
            # 使用PaddleOCR进行识别
            results = self.reader.ocr(image)
            
            # 解析结果
            parsed_results = self._parse_results(results)
            if not parsed_results:
                return None
            
            # 去除目标文字的空格，用于匹配
            target_text_stripped = target_text.replace(" ", "").replace("\u3000", "")
            
            for item in parsed_results:
                bbox, text, confidence = item
                
                # 去除识别文字的空格
                text_stripped = text.replace(" ", "").replace("\u3000", "")
                
                # 检查匹配
                matched = False
                if fuzzy:
                    # 模糊匹配：目标文字在识别文字中，或识别文字在目标文字中
                    matched = (target_text_stripped in text_stripped or 
                              text_stripped in target_text_stripped or
                              target_text in text or 
                              text in target_text)
                else:
                    # 精确匹配
                    matched = target_text_stripped == text_stripped
                
                if matched and confidence >= confidence_threshold:
                    # 计算中心点
                    bbox_array = np.array(bbox)
                    center_x = int(np.mean(bbox_array[:, 0]))
                    center_y = int(np.mean(bbox_array[:, 1]))
                    
                    logger.info(f"找到目标文字 '{target_text}': 实际文字='{text}' 位置=({center_x}, {center_y}), 置信度={confidence:.3f}")
                    return (center_x, center_y)
            
            logger.warning(f"未找到目标文字: '{target_text}'")
            return None
            
        except Exception as e:
            logger.error(f"查找文字失败: {e}")
            return None
    
    def get_all_text(self, image: np.ndarray) -> List[Tuple[str, Tuple[int, int], float]]:
        """获取图像中所有识别的文字
        
        Args:
            image: 输入图像
            
        Returns:
            所有文字列表，每项为 (文字, (中心x, 中心y), 置信度)
        """
        if self.reader is None:
            logger.error("OCR引擎未初始化")
            return []
        
        try:
            # 使用PaddleOCR进行识别
            results = self.reader.ocr(image)
            
            # 解析结果
            parsed_results = self._parse_results(results)
            
            all_text = []
            for bbox, text, confidence in parsed_results:
                
                bbox_array = np.array(bbox)
                center_x = int(np.mean(bbox_array[:, 0]))
                center_y = int(np.mean(bbox_array[:, 1]))
                all_text.append((text, (center_x, center_y), confidence))
            
            return all_text
            
        except Exception as e:
            logger.error(f"获取文字失败: {e}")
            return []
