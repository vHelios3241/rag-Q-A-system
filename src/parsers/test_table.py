import sys
from pathlib import Path

"""测试 TableProcessor 类"""

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.table_parser import TableProcessor


def test_markdown_to_dataframe():
  """测试 Markdown 表格转 DataFrame"""
  print("\n" + "=" * 50)
  print("测试 1: Markdown 表格转 DataFrame")
  print("=" * 50)

  processor = TableProcessor()

  # 测试用例 1: 简单表格
  simple_table = """| 姓名 | 年龄 | 城市 |
|---|---|---|
| 张三 | 25 | 北京 |
| 李四 | 30 | 上海 |"""

  df = processor.markdown_to_dataframe(simple_table)
  print("\n简单表格:")
  print(df)
  print(f"类型: {type(df)}, 形状: {df.shape if df is not None else None}")

  # 测试用例 2: 空表格
  empty_table = "| A | B |\n|---|---|"
  df_empty = processor.markdown_to_dataframe(empty_table)
  print("\n空表格 (只有表头):")
  print(df_empty)

  # 测试用例 3: 无效输入
  invalid = "不是表格"
  df_invalid = processor.markdown_to_dataframe(invalid)
  print(f"\n无效输入: {df_invalid}")


def test_dataframe_to_text():
  """测试 DataFrame 转文本"""
  print("\n" + "=" * 50)
  print("测试 2: DataFrame 转文本")
  print("=" * 50)

  processor = TableProcessor()

  table_md = """| 产品 | 价格 | 库存 |
|---|---|---|
| 手机 | 2999 | 100 |
| 电脑 | 5999 | 50 |
| 平板 | 1999 | 80 |"""

  df = processor.markdown_to_dataframe(table_md)
  text = processor.dataframe_to_text(df)
  print("\n文本输出:")
  print(text)


def test_table_to_text():
  """测试 Markdown 表格直接转文本"""
  print("\n" + "=" * 50)
  print("测试 3: Markdown 表格直接转文本")
  print("=" * 50)

  processor = TableProcessor()

  table_md = """| 科目 | 分数 |
|---|---|
| 语文 | 85 |
| 数学 | 92 |
| 英语 | 88 |"""

  text = processor.table_to_text(table_md)
  print("\n表格文本描述:")
  print(text)


def test_extract_key_value():
  """测试从表格提取键值对"""
  print("\n" + "=" * 50)
  print("测试 4: 从表格提取键值对")
  print("=" * 50)

  processor = TableProcessor()

  kv_table = """| 属性 | 值 |
|---|---|
| 姓名 | 王五 |
| 部门 | 技术部 |
| 职位 | 工程师 |
| 入职日期 | 2024-01-15 |"""

  result = processor.extract_key_value(kv_table)
  print("\n提取的键值对:")
  for key, value in result.items():
    print(f"  {key}: {value}")

  # 测试单列表格（应该返回空字典）
  single_col = "| A |\n|---|\n| 1 |\n| 2 |"
  result_single = processor.extract_key_value(single_col)
  print(f"\n单列表格结果: {result_single}")


def test_merge_tables():
  """测试合并跨页表格"""
  print("\n" + "=" * 50)
  print("测试 5: 合并跨页表格")
  print("=" * 50)

  processor = TableProcessor()

  # 模拟跨页表格
  tables = [
     {
      "table_number": 1,
      "page": 1,
      "cols": 3,
      "rows": 2,
      "markdown": "| 列1 | 列2 | 列3 |\n|---|---|---|\n| A1 | B1 | C1 |\n| A2 | B2 | C2 |"
     },
     {
      "table_number": 2,
      "page": 2,
      "cols": 3,
      "rows": 2,
      "markdown": "| 列1 | 列2 | 列3 |\n|---|---|---|\n| A3 | B3 | C3 |\n| A4 | B4 | C4 |"
     },
     {
      "table_number": 3,
      "page": 5, # 页码不连续，不合并
      "cols": 3,
      "rows": 2,
      "markdown": "| 列1 | 列2 | 列3 |\n|---|---|---|\n| X1 | Y1 | Z1 |"
     }
   ]

  print("\n合并前:")
  for t in tables:
    print(f"  页码 {t['page']}: {t['rows']} 行")

  merged = processor.merge_tables(tables)

  print("\n合并后:")
  for i, t in enumerate(merged, 1):
    print(f"  表格 {i}: 页码 {t['page']}, {t.get('rows', '?')} 行")

  # 测试单个表格
  single = [{"table_number": 1, "page": 1, "cols": 2, "markdown": "| A | B |"}]
  result = processor.merge_tables(single)
  print(f"\n单个表格合并: {len(result)} 个表格")


def test_edge_cases():
  """测试边界情况"""
  print("\n" + "=" * 50)
  print("测试 6: 边界情况")
  print("=" * 50)

  processor = TableProcessor()

  # 空字符串
  print("\n空字符串:")
  print(f"  结果: {processor.markdown_to_dataframe('')}")

  # 只有分隔线
  print("\n只有分隔线:")
  print(f"  结果: {processor.markdown_to_dataframe('|---|')}")

  # 单元格数量不一致
  print("\n单元格数量不一致:")
  bad_table = "| A | B |\n|---|---|\n| X | Y | Z |" # 2列表头，3列数据
  result = processor.markdown_to_dataframe(bad_table)
  print(f"  结果:\n{result}")

  # 空 DataFrame
  import pandas as pd
  empty_df = pd.DataFrame()
  print(f"\n空 DataFrame 转文本: '{processor.dataframe_to_text(empty_df)}'")


def main():
  """运行所有测试"""
  print("\n" + "=" * 60)
  print(" " * 15 + "TableProcessor 测试套件")
  print("=" * 60)

  test_markdown_to_dataframe()
  test_dataframe_to_text()
  test_table_to_text()
  test_extract_key_value()
  test_merge_tables()
  test_edge_cases()

  print("\n" + "=" * 60)
  print("所有测试完成!")
  print("=" * 60)


if __name__ == "__main__":
  main()
