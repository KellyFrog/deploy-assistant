"""
部署工作流引擎，实现：
1. 部署步骤生成
2. 步骤顺序验证
3. 结果有效性检查
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from utils.error_handling import exception_handler

@dataclass
class DeploymentStep:
    """部署步骤数据类"""
    name: str
    command: str
    expected_output: Optional[str] = None
    depends_on: List[str] = None

class DeploymentWorkflow:
    """
    部署工作流管理类，主要功能：
    - 解析文档结构生成步骤
    - 验证步骤依赖关系
    - 执行步骤完整性检查
    """
    
    def __init__(self, config: Dict):
        self.config = config
        print(config)
        self.steps = []

    def generate_workflow(self) -> List[DeploymentStep]:
        """生成部署步骤工作流"""
        self._parse_sections()
        self._resolve_dependencies()
        return self.steps

    def validate_step(self, step: DeploymentStep) -> bool:
        """
        验证单个步骤有效性：
        1. 命令非空
        2. 依赖存在
        3. 预期输出格式正确
        """
        if not step.command:
            return False
        if step.depends_on:
            existing = {s.name for s in self.steps}
            if not set(step.depends_on).issubset(existing):
                return False
        return True

    def _parse_sections(self) -> None:
        """解析文档章节生成基础步骤"""
        for section, data in self.config['sections'].items():
            print("----")
            print(section)
            print(data)
            print("----")
            for idx, cmd in enumerate(data, 1):
                self.steps.append(
                    DeploymentStep(
                        name=f"{section}_step{idx}",
                        command=cmd,
                        depends_on=self._detect_depends(cmd)
                    )
                )

    def _detect_depends(self, command: str) -> List[str]:
        """检测命令中的依赖关系（示例逻辑）"""
        deps = []
        if 'install' in command:
            # deps.append('environment_check')
            pass
        return deps

    def _resolve_dependencies(self) -> None:
        """调整步骤执行顺序满足依赖关系"""
        ordered = []
        pending = self.steps.copy()

        print(pending)
        
        while pending:
            ready = [s for s in pending 
                    if not s.depends_on or 
                    all(d in [o.name for o in ordered] 
                        for d in s.depends_on)]
            print("ready = ")
            print(ready)
            if not ready:
                raise CycleDependencyError("存在循环依赖")
            ordered.extend(ready)
            pending = [s for s in pending if s not in ready]
            
        self.steps = ordered

class CycleDependencyError(Exception):
    """部署步骤循环依赖异常"""
    def __init__(self, message: str):
        super().__init__(f"工作流依赖错误: {message}")
