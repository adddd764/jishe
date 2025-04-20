
# Tau蛋白自噬调控通路知识图谱构建系统README

## 一、系统概述
本系统围绕Tau蛋白自噬调控通路，整合多源生物医学数据，通过数据爬取、清洗、结构化处理及知识图谱构建，实现对通路相关实体（基因、化合物、疾病等）及其关系的可视化建模。系统包含数据采集、处理、分析及图谱搭建全流程工具链，支持从文献和数据库中提取关键信息并构建可交互的知识网络。


## 二、系统文件结构
| 文件/文件夹         | 功能描述                                                                 |
|--------------------|--------------------------------------------------------------------------|
| `program.json`      | 核心实体数据文件，存储基因、化合物、实验方法等节点的属性及关系信息         |
| `data.json`         | 扩展数据文件，包含更多疾病关联、调控机制及实验模型数据                     |
| `deny.txt`          | 敏感词过滤列表，用于文本清洗和合规性检查                                  |
| `TauClear.yml`      | 工作流配置文件，定义自动化分析流程的节点和执行逻辑                        |
| `web.html`          | 前端展示页面，实现阿尔茨海默病科普内容的可视化及用户交互                  |
| `Web_spider.py`     | 数据爬取脚本，支持PubMed、ScienceDirect等数据库的文献下载                 |
| `data_clean.py`     | PDF文本清洗工具，包含文本提取、去噪、分句及词形还原等预处理功能          |
| `build_graph.py`    | 知识图谱构建脚本，基于Neo4j构建实体关系图                                 |
| `数据结构化.yml`    | 数据结构化配置文件，定义从文献中提取实体的规则和输出格式                  |
| `medical_doc/`      | 原始文献存储文件夹，自动保存爬取的PDF文献                                 |
| `medical_doc_cleaned/` | 清洗后文献存储文件夹，保存预处理后的文本数据                       |


## 三、核心功能模块

### 1. 数据爬取模块（`Web_spider.py`）
- **功能**：从PubMed、ScienceDirect、IEEE Xplore等学术数据库搜索并下载与Tau蛋白自噬相关的文献PDF。
- **使用方法**：
  ```python
  # 修改关键词和下载数量
  query = "Alzheimer’s Disease; Autophagy; Tau Protein"  # 搜索关键词，支持布尔逻辑
  retmax = 5  # 下载文献数量
  # 执行爬取
  python Web_spider.py
  ```
- **依赖工具**：
  - `requests`：HTTP请求库
  - `selenium`：浏览器自动化工具（需配置ChromeDriver）
  - `Bio`：NCBI Entrez接口
  -由于权限问题，只选择爬取标题作者摘要，然后进行人工收集 


### 2. 文本清洗模块（`data_clean.py`）
- **功能**：对爬取的PDF文献进行文本提取、去除页眉页脚/参考文献、清洗特殊字符及自然语言处理（NLP）。
- **处理流程**：
  ```
  原始PDF → 文本提取 → 去除干扰内容 → 小写转换 → 分句 → 停用词过滤 → 词形还原 → 保存清洗后PDF
  ```
- **关键函数**：
  - `extract_text_from_pdf()`：基于PyMuPDF提取文本
  - `clean_text()`：正则表达式清洗文本
  - `lemmatize_sentences()`：基于NLTK进行词形还原


### 3. 数据结构化模块（`数据结构化.yml`）
- **功能**：通过LLM（如DeepSeek-R1）从清洗后的文本中提取实体（基因、化合物、通路等）及其关系，生成标准化JSON。
- **配置说明**：
  - `document-extractor`：指定输入文件类型（PDF/文本）
  - `LLM`：定义实体提取规则，支持KEGG通路、HGNC基因命名等标准
  - `输出示例`：
    ```json
    {
      "_id": {"$oid": "5bb578b6831b973a137e3ee6"},
      "name": "ULK1",
      "type": "核心基因",
      "uniprot_id": "P10636",
      "modifications": [{"type": "磷酸化修饰", "site": "Ser356"}],
      "related_pathway": "Tau蛋白自噬调控通路"
    }
    ```


### 4. 知识图谱构建模块（`build_graph.py`）
- **功能**：基于Neo4j构建Tau蛋白自噬调控通路知识图谱，包含节点（化合物、基因、疾病等）及关系（作用靶点、参与通路、关联疾病等）。
- **节点类型**：
  - `Compound`：调控化合物（如雷帕霉素、西罗莫司）
  - `Gene`：核心基因（如ULK1、BECN1）
  - `Pathway`：信号通路（如hsa04140、Tau蛋白自噬调控通路）
  - `Disease`：关联疾病（如阿尔茨海默病、额颞叶痴呆）
- **关系类型**：
  - `targets`：化合物→靶点（基因/蛋白质）
  - `involved_in`：实体→参与通路
  - `assoc_with`：基因/蛋白质→关联疾病
- **运行命令**：
  ```python
  python build_graph.py  # 需提前配置Neo4j连接参数（bolt://localhost:7687，用户名/密码）
  ```


### 5. 前端展示模块（`web.html`）
- **功能**：提供阿尔茨海默病科普页面，包含疾病介绍、诊断治疗、预防指南及知识图谱可视化入口。
- **技术栈**：
  - HTML/CSS：基于Tailwind CSS实现响应式布局
  - JavaScript：集成Mermaid绘制病理流程图
  - 聊天机器人：通过Dify嵌入智能问答功能
- **页面结构**：
  - 导航栏：疾病、诊断、治疗、预防
  - 统计卡片：全球患者数量、疾病危害、治疗难点
  - 动态图表：展示Tau蛋白与β淀粉样蛋白的病理关系
  - 治疗方案：药物治疗（胆碱酯酶抑制剂等）、非药物干预


## 四、系统依赖与安装
### 1. 环境依赖
- **Python库**：
  ```bash
  pip install requests beautifulsoup4 pymongo lxml selenium py2neo nltk fitz reportlab
  ```
- **工具**：
  - ChromeDriver：用于Selenium驱动浏览器（需匹配本地Chrome版本）
  - Neo4j数据库：版本≥4.0，需创建数据库并配置认证信息
  - LLM模型：通过Ollama部署`deepseek-r1:7b`模型


### 2. 配置文件说明
- **`TauClear.yml` & `数据结构化.yml`**：
  - 定义工作流节点顺序（如文献提取→LLM解析→图谱构建）
  - 配置工具参数（如PubMed搜索关键词、Neo4j连接URL）
- **`build_graph.py`**：
  ```python
  self.g = Graph("bolt://localhost:7687", auth=("neo4j", "your_password"))  # 修改为实际数据库密码
  self.data_path = "path/to/your/data.json"  # 指定实体数据文件路径
  ```


## 五、使用流程
1. **数据爬取**：运行`Web_spider.py`下载相关文献PDF。
2. **文本清洗**：执行`data_clean.py`生成预处理后的文本。
3. **结构化提取**：通过`数据结构化.yml`工作流提取实体关系，生成JSON数据。
4. **图谱构建**：运行`build_graph.py`将JSON数据导入Neo4j，生成知识图谱。
5. **前端展示**：打开`web.html`查看科普内容，通过Neo4j浏览器访问图谱可视化界面。


## 六、注意事项
1. **合规性**：
   - 遵守各数据库的爬取规则（如PubMed的robots.txt）。
   - 避免爬取受版权保护的文献全文，仅用于学术研究。
2. **性能优化**：
   - 增加`Web_spider.py`中的请求间隔（`time.sleep(5)`），避免IP封禁。
   - 对大规模数据分批次处理，避免内存溢出。
3. **模型配置**：
   - 确保LLM模型正确加载，可通过Ollama调整`deepseek-r1:7b`的温度参数（`temperature: 0.2`）提升解析准确性。


## 七、故障排除
| 问题描述                          | 解决方案                                                                 |
|-----------------------------------|--------------------------------------------------------------------------|
| `requests.exceptions.ConnectionError` | 检查网络连接，添加代理服务器或更换爬取时间                                |
| `selenium.common.exceptions.WebDriverException` | 确认ChromeDriver路径正确，或升级Chrome浏览器                              |
| `Neo4j连接失败`                   | 检查Neo4j服务是否启动，认证信息是否正确                                  |
| `LLM解析结果为空`                 | 调整提示词（prompt），增加示例输入或提高模型温度参数                      |


## 八、联系方式
- **邮箱**：
- **项目地址**：

通过本系统，用户可快速构建Tau蛋白自噬调控通路的知识图谱，支持阿尔茨海默病相关研究的数据整合与可视化分析。如需定制功能或报告问题，请参考上述联系方式。
