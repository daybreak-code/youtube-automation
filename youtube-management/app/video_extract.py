import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import logging
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class SceneInfo:
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    keyframe: np.ndarray
    scene_type: str
    
class VideoSceneExtractor:
    def __init__(self, 
                 min_scene_duration: float = 1.0,  # 最小场景时长(秒)
                 similarity_threshold: float = 0.7,  # 场景相似度阈值
                 check_frames: int = 30  # 场景变化前后检查帧数
                ):
        self.min_scene_duration = min_scene_duration
        self.similarity_threshold = similarity_threshold
        self.check_frames = check_frames
        self.logger = logging.getLogger(__name__)

    def extract_scenes(self, video_path: str) -> List[SceneInfo]:
        """提取视频场景"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")

        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        min_scene_frames = int(self.min_scene_duration * fps)

        scenes = []
        frames_buffer = []
        current_scene_start = 0
        prev_frame = None
        
        self.logger.info(f"开始处理视频: {video_path}")
        self.logger.info(f"FPS: {fps}, 总帧数: {frame_count}")

        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 将帧添加到缓冲区
            frames_buffer.append(frame)
            if len(frames_buffer) > self.check_frames * 2:
                frames_buffer.pop(0)

            if prev_frame is not None:
                # 计算与前一帧的相似度
                similarity = self.calculate_frame_similarity(prev_frame, frame)
                
                # 如果相似度低于阈值且当前场景长度大于最小场景时长
                if similarity < self.similarity_threshold and frame_idx - current_scene_start >= min_scene_frames:
                    # 从缓冲区中选择最清晰的关键帧
                    keyframe = self.find_best_keyframe(frames_buffer)
                    
                    scene = SceneInfo(
                        start_frame=current_scene_start,
                        end_frame=frame_idx,
                        start_time=current_scene_start / fps,
                        end_time=frame_idx / fps,
                        keyframe=keyframe,
                        scene_type=self.detect_scene_type(keyframe)
                    )
                    scenes.append(scene)
                    current_scene_start = frame_idx

            prev_frame = frame.copy()
            frame_idx += 1

        # 处理最后一个场景
        if frame_idx - current_scene_start >= min_scene_frames:
            keyframe = self.find_best_keyframe(frames_buffer)
            scenes.append(SceneInfo(
                start_frame=current_scene_start,
                end_frame=frame_idx,
                start_time=current_scene_start / fps,
                end_time=frame_idx / fps,
                keyframe=keyframe,
                scene_type=self.detect_scene_type(keyframe)
            ))

        cap.release()
        self.logger.info(f"场景提取完成，共找到 {len(scenes)} 个场景")
        return scenes

    def calculate_frame_similarity(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """计算两帧之间的相似度"""
        # 转换为灰度图
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # 计算结构相似度
        ssim = self.calculate_ssim(gray1, gray2)
        
        # 计算颜色直方图相似度
        hist_sim = self.calculate_histogram_similarity(frame1, frame2)
        
        # 综合相似度
        return 0.6 * ssim + 0.4 * hist_sim

    def calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """计算结构相似度"""
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2

        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)
        kernel = cv2.getGaussianKernel(11, 1.5)
        window = np.outer(kernel, kernel.transpose())

        mu1 = cv2.filter2D(img1, -1, window)[5:-5, 5:-5]
        mu2 = cv2.filter2D(img2, -1, window)[5:-5, 5:-5]
        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2
        sigma1_sq = cv2.filter2D(img1 ** 2, -1, window)[5:-5, 5:-5] - mu1_sq
        sigma2_sq = cv2.filter2D(img2 ** 2, -1, window)[5:-5, 5:-5] - mu2_sq
        sigma12 = cv2.filter2D(img1 * img2, -1, window)[5:-5, 5:-5] - mu1_mu2

        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
                   ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
        return ssim_map.mean()

    def calculate_histogram_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """计算颜色直方图相似度"""
        hist1 = cv2.calcHist([img1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist2 = cv2.calcHist([img2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        
        # 归一化直方图
        cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
        
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    def find_best_keyframe(self, frames: List[np.ndarray]) -> np.ndarray:
        """从帧缓冲区中找到最清晰的关键帧"""
        max_variance = -1
        best_frame = None
        
        for frame in frames:
            # 计算拉普拉斯方差（清晰度度量）
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if variance > max_variance:
                max_variance = variance
                best_frame = frame
        
        return best_frame

    def detect_scene_type(self, frame: np.ndarray) -> str:
        """检测场景类型"""
        # 这里实现一个简单的场景类型检测
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_ratio = np.count_nonzero(edges) / edges.size
        
        if edge_ratio > 0.1:
            return "特写" if edge_ratio > 0.2 else "远景"
        else:
            return "室内" if np.mean(gray) < 127 else "室外"

    def save_scene_keyframes(self, scenes: List[SceneInfo], output_dir: str):
        """保存场景关键帧"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, scene in enumerate(scenes):
            timestamp = str(timedelta(seconds=int(scene.start_time)))
            filename = f"scene_{i+1}_{timestamp}_{scene.scene_type}.jpg"
            cv2.imwrite(str(output_path / filename), scene.keyframe)

def extract_video_scenes(video_path: str, output_dir: str, 
                        min_scene_duration: float = 1.0,
                        similarity_threshold: float = 0.7,
                        check_frames: int = 30) -> List[SceneInfo]:
    """提取视频场景的便捷函数"""
    extractor = VideoSceneExtractor(
        min_scene_duration=min_scene_duration,
        similarity_threshold=similarity_threshold,
        check_frames=check_frames
    )
    
    scenes = extractor.extract_scenes(video_path)
    extractor.save_scene_keyframes(scenes, output_dir)
    return scenes 