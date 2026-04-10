# -*- coding: utf-8 -*-
"""
多智能体协作编排系统
架构: Orchestrator(调度器) -> Workers(并行)
协程方案: asyncio + httpx，用于 I/O 密集型 LLM 调用
Worker间通信: asyncio.Queue + 共享字典
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ─── Worker 类型枚举 ───────────────────────────────────────
class WorkerType(Enum):
    BAZI_PAN    = "bazi_pan"
    OTHER_FATE  = "other_fate"
    LIBRARY     = "library"
    LLM解读     = "llm"


# ─── 任务封装 ───────────────────────────────────────────
@dataclass
class Task:
    task_id: str
    worker_type: WorkerType
    input_data: Dict[str, Any]
    priority: int = 5  # 1=最高，10=最低
    timeout_sec: float = 30.0


@dataclass
class TaskResult:
    task_id: str
    worker_type: WorkerType
    success: bool
    data: Any = None
    error: Optional[str] = None
    elapsed_sec: float = 0.0


# ─── Worker 基类 ──────────────────────────────────────────
class BaseWorker:
    """Worker 基类，定义通用接口"""

    def __init__(self, name: str, worker_type: WorkerType):
        self.name = name
        self.worker_type = worker_type

    async def execute(self, task: Task) -> TaskResult:
        """同步入口，由 Orchestrator 在协程中调度"""
        raise NotImplementedError

    async def health_check(self) -> bool:
        """健康检查"""
        return True


# ─── Worker 1: 八字排盘（确定性规则引擎）───────────────
class BaziPanWorker(BaseWorker):
    """八字排盘 Worker — 确定性规则引擎，无 LLM 调用"""

    def __init__(self):
        super().__init__("八字排盘", WorkerType.BAZI_PAN)
        # 延迟导入避免循环依赖
        self._engine = None

    @property
    def engine(self):
        if self._engine is None:
            from backend.services import engine
            self._engine = engine
        return self._engine

    async def execute(self, task: Task) -> TaskResult:
        t0 = time.time()
        try:
            params = task.input_data
            result = self.engine.bazi_pan(
                year=params["year"],
                month=params["month"],
                day=params["day"],
                hour=params["hour"],
                gender=params.get("gender", "男"),
                location=params.get("location", "北京"),
            )
            return TaskResult(
                task_id=task.task_id,
                worker_type=self.worker_type,
                success=True,
                data=result,
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:
            logger.exception(f"BaziPanWorker failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                worker_type=self.worker_type,
                success=False,
                error=str(e),
                elapsed_sec=time.time() - t0,
            )


# ─── Worker 2: 其他术数（紫微/奇门）并行计算 ─────────────
class OtherFateWorker(BaseWorker):
    """紫微斗数 / 奇门遁甲并行计算 Worker"""

    def __init__(self):
        super().__init__("其他术数", WorkerType.OTHER_FATE)
        self._plugins = None

    def _load_plugins(self):
        if self._plugins is None:
            try:
                from backend.plugins import PluginRegistry
                registry = PluginRegistry()
                if not registry.list_all():
                    registry.discover()
                self._plugins = {p.name: p for p in registry.list_all()}
            except ImportError:
                self._plugins = {}
                logger.warning("Plugin system not available, using builtins")

    async def execute(self, task: Task) -> TaskResult:
        t0 = time.time()
        try:
            self._load_plugins()
            pillar_data = task.input_data.get("pillar_data", {})
            target_plugins = task.input_data.get("plugins", ["qimen", "ziwei"])
            results = {}
            # 并发执行多个插件（asyncio.gather）
            plugin_tasks = []
            plugin_names = []
            for name in target_plugins:
                plugin = self._plugins.get(name)
                if plugin:
                    plugin_tasks.append(self._run_plugin(plugin, pillar_data))
                    plugin_names.append(name)
            if plugin_tasks:
                plugin_results = await asyncio.gather(*plugin_tasks, return_exceptions=True)
                for name, result in zip(plugin_names, plugin_results):
                    if isinstance(result, Exception):
                        results[name] = {"error": str(result)}
                    else:
                        results[name] = result
            return TaskResult(
                task_id=task.task_id,
                worker_type=self.worker_type,
                success=True,
                data=results,
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:
            logger.exception(f"OtherFateWorker failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                worker_type=self.worker_type,
                success=False,
                error=str(e),
                elapsed_sec=time.time() - t0,
            )

    async def _run_plugin(self, plugin, pillar_data):
        return plugin.analyze(pillar_data)


# ─── Worker 3: 书库检索（RAG）───────────────────────────────
class LibraryWorker(BaseWorker):
    """古籍书库 RAG 检索 Worker"""

    def __init__(self):
        super().__init__("书库检索", WorkerType.LIBRARY)
        self._index = None
        self._chunk_store = None
        # 书库路径（可配置）
        self.corpus_path = r"C:\Users\Administrator\WorkBuddy\20260409001107\书库\语料库\分类汇总"

    async def execute(self, task: Task) -> TaskResult:
        t0 = time.time()
        try:
            query = task.input_data.get("query", "")
            pillar_data = task.input_data.get("pillar_data", {})
            top_k = task.input_data.get("top_k", 5)
            # 组合关键词查询
            keywords = self._extract_keywords(pillar_data)
            results = await self._search_corpus(query, keywords, top_k)
            return TaskResult(
                task_id=task.task_id,
                worker_type=self.worker_type,
                success=True,
                data={"chunks": results, "keywords": keywords},
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:
            logger.exception(f"LibraryWorker failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                worker_type=self.worker_type,
                success=False,
                error=str(e),
                elapsed_sec=time.time() - t0,
            )

    def _extract_keywords(self, pillar_data: Dict) -> List[str]:
        """从八字数据中提取关键词用于书库检索"""
        keywords = []
        pillar = pillar_data.get("pillar", {})
        for key in ["year", "month", "day", "time"]:
            zhu = pillar.get(key, "")
            if zhu:
                keywords.extend(list(zhu))
        wuxing = pillar_data.get("wuxing", {})
        keywords.extend(wuxing.get("xiyongshen", []))
        keywords.extend(wuxing.get("jishen", []))
        geju = pillar_data.get("geju", {})
        if geju:
            keywords.append(geju.get("name", ""))
        return list(set(keywords))[:10]

    async def _search_corpus(self, query: str, keywords: List[str], top_k: int) -> List[Dict]:
        """
        全文检索方案（轻量级，无需向量数据库）：
        1. 解析语料库文本（已按书籍分节，含标题行）
        2. 用关键词 + 查询词做行级匹配评分
        3. 返回 top_k 条最相关段落
        """
        import pathlib
        results = []
        corpus_root = pathlib.Path(self.corpus_path)
        if not corpus_root.exists():
            logger.warning(f"Corpus path not found: {corpus_root}")
            return results
        score_map = {}
        for txt_file in corpus_root.glob("*.txt"):
            try:
                with open(txt_file, encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
            except Exception:
                continue
            for i, line in enumerate(lines):
                if len(line.strip()) < 10:
                    continue
                score = 0
                for kw in keywords:
                    if kw in line:
                        score += 1
                for qw in query:
                    if qw in line:
                        score += 0.5
                if score > 0:
                    key = f"{txt_file.stem}:{i}"
                    if key not in score_map or score_map[key]["score"] < score:
                        score_map[key] = {"score": score, "line": line.strip(), "source": txt_file.stem, "line_num": i+1}
        sorted_chunks = sorted(score_map.values(), key=lambda x: x["score"], reverse=True)
        return sorted_chunks[:top_k]


# ─── Worker 4: LLM 解读 ────────────────────────────────────
class LLMWorker(BaseWorker):
    """LLM 综合解读 Worker — 整合所有 Worker 结果生成解读"""

    def __init__(self):
        super().__init__("LLM解读", WorkerType.LLM)
        self._llm_service = None

    @property
    def llm_service(self):
        if self._llm_service is None:
            from backend.services.llm_service import get_llm_service
            self._llm_service = get_llm_service()
        return self._llm_service

    async def execute(self, task: Task) -> TaskResult:
        t0 = time.time()
        try:
            combined = task.input_data
            pillar_data = combined.get("pillar_data", {})
            plugin_results = combined.get("plugin_results", {})
            corpus_chunks = combined.get("corpus_chunks", [])
            user_query = combined.get("user_query", "")
            style = combined.get("style", "professional")
            # 构建增强 Prompt
            system_prompt, user_prompt = self._build_enhanced_prompt(
                pillar_data, plugin_results, corpus_chunks, user_query, style
            )
            # 异步调用 LLM
            report = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.llm_service.chat(system_prompt, user_prompt)
            )
            return TaskResult(
                task_id=task.task_id,
                worker_type=self.worker_type,
                success=True,
                data={"report": report, "prompt": {"system": system_prompt, "user": user_prompt}},
                elapsed_sec=time.time() - t0,
            )
        except Exception as e:
            logger.exception(f"LLMWorker failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                worker_type=self.worker_type,
                success=False,
                error=str(e),
                elapsed_sec=time.time() - t0,
            )

    def _build_enhanced_prompt(self, pillar, plugins, chunks, query, style):
        from backend.services.engine import build_llm_prompt
        sys_p, usr_p = build_llm_prompt(pillar, query, style)
        # 追加古籍引用
        if chunks:
            refs = "\n".join([f"【{c['source']}】{c['line'][:200]}" for c in chunks[:3]])
            usr_p += f"\n\n【古籍参考】\n{refs}"
        # 追加插件结果摘要
        if plugins:
            plugin_summaries = []
            for name, res in plugins.items():
                if isinstance(res, dict) and "summary" in res:
                    plugin_summaries.append(f"【{name}】{res['summary']}")
            if plugin_summaries:
                usr_p += f"\n\n【其他术数参考】\n" + "\n".join(plugin_summaries)
        return sys_p, usr_p


# ─── Orchestrator 调度器 ──────────────────────────────────
class Orchestrator:
    """
    多智能体调度器
    执行流程：
    1. 接收请求，拆解任务
    2. Worker1（八字排盘）先执行（必须）
    3. Worker2（紫微/奇门）并行执行（依赖Worker1结果）
    4. Worker3（书库检索）并行执行（依赖Worker1结果）
    5. Worker4（LLM解读）最后执行（依赖Worker1+2+3结果）
    6. 汇总结果返回
    """

    def __init__(self):
        self.bazi_worker = BaziPanWorker()
        self.fate_worker = OtherFateWorker()
        self.library_worker = LibraryWorker()
        self.llm_worker = LLMWorker()
        self._task_counter = 0

    def _new_task_id(self) -> str:
        self._task_counter += 1
        return f"task_{int(time.time()*1000)}_{self._task_counter}"

    async def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        主入口：执行完整分析流程
        params: {year, month, day, hour, gender, location, plugins, query, style}
        """
        start_time = time.time()
        pillar_data = None
        plugin_results = {}
        corpus_chunks = []
        llm_report = ""
        errors = {}
        worker_times = {}

        try:
            # ── 阶段1: 八字排盘（串行，必须先执行）─────────────
            bazi_task = Task(
                task_id=self._new_task_id(),
                worker_type=WorkerType.BAZI_PAN,
                input_data=params,
                priority=1,
                timeout_sec=10.0,
            )
            bazi_result = await self._run_worker(bazi_task, self.bazi_worker)
            if bazi_result.success:
                pillar_data = bazi_result.data
                worker_times["bazi_pan"] = bazi_result.elapsed_sec
            else:
                errors["bazi_pan"] = bazi_result.error
                raise RuntimeError(f"八字排盘失败: {bazi_result.error}")

            # ── 阶段2: 其他术数 & 书库检索（并行）─────────────
            target_plugins = params.get("plugins", ["qimen", "ziwei"])
            fate_task = Task(
                task_id=self._new_task_id(),
                worker_type=WorkerType.OTHER_FATE,
                input_data={"pillar_data": pillar_data, "plugins": target_plugins},
                priority=2,
                timeout_sec=15.0,
            )
            lib_task = Task(
                task_id=self._new_task_id(),
                worker_type=WorkerType.LIBRARY,
                input_data={"pillar_data": pillar_data, "query": params.get("query", ""), "top_k": 5},
                priority=3,
                timeout_sec=10.0,
            )
            # asyncio.gather 并行
            fate_result, lib_result = await asyncio.gather(
                self._run_worker(fate_task, self.fate_worker),
                self._run_worker(lib_task, self.library_worker),
                return_exceptions=True,
            )
            if not isinstance(fate_result, Exception) and fate_result.success:
                plugin_results = fate_result.data
                worker_times["other_fate"] = fate_result.elapsed_sec
            elif isinstance(fate_result, Exception):
                errors["other_fate"] = str(fate_result)
            if not isinstance(lib_result, Exception) and lib_result.success:
                corpus_chunks = lib_result.data.get("chunks", [])
                worker_times["library"] = lib_result.elapsed_sec
            elif isinstance(lib_result, Exception):
                errors["library"] = str(lib_result)

            # ── 阶段3: LLM 解读（最后执行）─────────────────────
            llm_task = Task(
                task_id=self._new_task_id(),
                worker_type=WorkerType.LLM,
                input_data={
                    "pillar_data": pillar_data,
                    "plugin_results": plugin_results,
                    "corpus_chunks": corpus_chunks,
                    "user_query": params.get("query", ""),
                    "style": params.get("style", "professional"),
                },
                priority=4,
                timeout_sec=60.0,
            )
            llm_result = await self._run_worker(llm_task, self.llm_worker)
            if llm_result.success:
                llm_report = llm_result.data.get("report", "")
                worker_times["llm"] = llm_result.elapsed_sec
            else:
                errors["llm"] = llm_result.error
                llm_report = f"【系统提示】LLM解读暂时不可用：{llm_result.error}"

        except Exception as e:
            logger.exception(f"Orchestrator.run failed: {e}")
            errors["orchestrator"] = str(e)

        return {
            "success": pillar_data is not None,
            "total_elapsed_sec": round(time.time() - start_time, 2),
            "worker_times": worker_times,
            "pillar_data": pillar_data,
            "plugin_results": plugin_results,
            "corpus_chunks": corpus_chunks,
            "llm_report": llm_report,
            "errors": errors,
        }

    async def _run_worker(self, task: Task, worker: BaseWorker) -> TaskResult:
        """使用 asyncio.timeout 包装 Worker 执行，实现超时控制"""
        try:
            async with asyncio.timeout(task.timeout_sec):
                return await worker.execute(task)
        except asyncio.TimeoutError:
            logger.warning(f"Worker {worker.name} timed out after {task.timeout_sec}s")
            return TaskResult(
                task_id=task.task_id,
                worker_type=task.worker_type,
                success=False,
                error=f"Timeout after {task.timeout_sec}s",
            )
        except Exception as e:
            logger.exception(f"Worker {worker.name} exception: {e}")
            return TaskResult(
                task_id=task.task_id,
                worker_type=task.worker_type,
                success=False,
                error=str(e),
            )


# ─── 全局单例 ────────────────────────────────────────────
_orchestrator: Optional[Orchestrator] = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
