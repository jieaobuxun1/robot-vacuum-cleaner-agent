"""命令行入口：构建/增量更新向量知识库。

用法（在项目根目录执行）：
    python -m rag.build_index
"""

from rag.vector_store import VectorStoreService
from utils.logger_handler import logger


def main() -> int:
    service = VectorStoreService()
    before = service.count_documents()

    try:
        service.load_document()
    except Exception as e:
        logger.error(f"[构建知识库]执行失败：{str(e)}", exc_info=True)
        return 1

    total = service.count_documents()
    if total == 0:
        logger.error("[构建知识库]知识库仍为空，请检查 data 目录下是否存在可解析的 txt/pdf 文件")
        return 1

    logger.info(f"[构建知识库]完成：本次新增{total - before}个片段，当前共{total}个片段")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
