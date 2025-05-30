
# Tau蛋白自噬调控通路知识图谱构建系统README

## 一、系统概述
本系统围绕Tau蛋白自噬调控通路，整合多源生物医学数据，通过数据爬取、清洗、结构化处理及知识图谱构建，实现对通路相关实体（基因、化合物、疾病等）及其关系的可视化建模。系统包含数据采集、处理、分析及图谱搭建全流程工具链，支持从文献和数据库中提取关键信息并构建可交互的知识网络。


## 二、系统文件结构
| 文件/文件夹         | 功能描述                                                                 |
|--------------------|--------------------------------------------------------------------------|
| `data.json`         | 扩展数据文件，包含更多疾病关联、调控机制及实验模型数据                       |
| `deny.txt`          | 敏感词过滤列表，用于文本清洗和合规性检查                                   |
| `TauClear.yml`      | 工作流配置文件，定义自动化分析流程的节点和执行逻辑                          |
| `web.html`          | 前端展示页面，实现阿尔茨海默病科普内容的可视化及用户交互                    |
| `Web_spider.py`     | 数据爬取脚本，支持PubMed、ScienceDirect等数据库的文献下载                 |
| `data_clean.py`     | PDF文本清洗工具，包含文本提取、去噪、分句及词形还原等预处理功能             |
| `build_graph.py`    | 知识图谱构建脚本，基于Neo4j构建实体关系图                                 |
| `数据结构化.yml`    | 数据结构化配置文件，定义从文献中提取实体的规则和输出格式                     |
| `medical_doc/`      | 原始文献存储文件夹，自动保存爬取的PDF文献                                 |
| `medical_doc_cleaned/` | 清洗后文献存储文件夹，保存预处理后的文本数据                            |

注：medical_doc只展示了少部分原始文献，具体内容通过可通过百度网盘提取
链接: https://pan.baidu.com/s/1UooCaatTwlcX3hvLdmMicw?pwd=wdau 提取码: wdau 



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
- **功能**：基于 Neo4j 构建 Tau 蛋白自噬调控通路知识图谱，包含节点（化合物、基因、疾病等）及关系（作用靶点、参与通路、关联疾病等）。系统框架图展示了整体工作流程，用户输入自然语言问句后，经过医疗实体识别、实体 / 问句关系抽取等步骤，最终基于 neo4j 图形数据库进行知识库答案检索。

     <img width="471" alt="8fadd0ec6c4293ae5b4f34728d194f9" src="https://github.com/user-attachments/assets/bde03b24-2617-48e8-a5fd-4b82731630fa" />


- **节点类型**：
  - `Compound`：调控化合物（如雷帕霉素、西罗莫司）
  - `Gene`：核心基因（如ULK1、BECN1）
  - `Pathway`：信号通路（如hsa04140、Tau蛋白自噬调控通路）
  - `Disease`：关联疾病（如阿尔茨海默病、额颞叶痴呆）
- **关系类型**：
  - `targets`：化合物→靶点（基因/蛋白质）
  - `involved_in`：实体→参与通路
  - `assoc_with`：基因/蛋白质→关联疾病
  - 以下为知识图谱示例，展示了不同实体之间的关系：
  - 知识图谱 1：这张图谱展示了多种实体间的复杂关联。可以看到不同颜色的节点代表不同类型的实体，如基因、化合物等。节点之间的连线表示它们的关系，例如某些基因与化合物之间存在调控关系，反映了在 Tau 蛋白自噬调控通路中，化合物可能通过作用于特定基因来影响通路的运行。这些关系是基于生物医学研究文献和实验数据提取构建的，为深入理解通路机制提供了直观的可视化呈现。
    
  <img width="868" alt="d57520ca07e5af58b198aa4cd6360b3" src="https://github.com/user-attachments/assets/b62780b5-9a9f-48f6-9746-70fee9902e1f" />
  
  知识图谱 2：该图谱聚焦于部分基因、化合物与疾病之间的联系。从中能够观察到特定基因与疾病的关联，以及化合物在其中可能起到的干预作用。比如，某些基因的异常表达可能与阿尔茨海默病等疾病相关，而化合物可能通过调节这些基因的表达来影响疾病进程。图谱清晰地呈现了这些实体和关系，有助于研究人员挖掘潜在的治疗靶点和干预策略。

  <img width="750" alt="df64da36a96034416d81d4a11786b73" src="https://github.com/user-attachments/assets/299821d7-8b09-4d23-a375-c53d4c9f5c53" />
  
  知识图谱 3：此图谱进一步展示了不同实体的相互作用网络。在 Tau 蛋白自噬调控通路的背景下，体现了基因、化合物之间的协同或拮抗关系。例如，一些基因之间可能存在相互调控，而化合物可能会影响这种调控关系。通过对该图谱的分析，可以探索通路中各要素的动态变化，为相关疾病的研究和药物研发提供线索。
  
  <img width="846" alt="4c49af91db76ac5b4c55bfbf443ddcf" src="https://github.com/user-attachments/assets/19b50e4c-3943-4a97-aea2-c6dfa316a25a" />

- **运行命令**：
  ```python
  python build_graph.py  # 需提前配置Neo4j连接参数（bolt://localhost:7687，用户名/密码）
  ```


### 5. 前端展示模块（`web.html`）
- **功能**：提供阿尔茨海默病科普页面，包含疾病介绍、诊断治疗、预防指南及知识图谱可视化入口。网页界面如下，提供了关于阿尔茨海默病的相关信息，包括患者数量、疾病危害、治疗难点等统计信息，同时集成了 TauClear 智能问答助手，方便用户咨询相关问题。
- ![fc71e2ef87fefb00696d527f7f5d783](https://github.com/user-attachments/assets/00333c12-65bd-4a1b-a007-e843e3f5e14b)

- **技术栈**：
  - HTML/CSS：基于Tailwind CSS实现响应式布局
  - JavaScript：集成Mermaid绘制病理流程图
  - 聊天机器人：通过Dify嵌入智能问答功能
- **页面结构**：
  - 导航栏：疾病、诊断、治疗、预防
  - 统计卡片：全球患者数量、疾病危害、治疗难点
  - 动态图表：展示Tau蛋白与β淀粉样蛋白的病理关系
  - 治疗方案：药物治疗（胆碱酯酶抑制剂等）、非药物干预
 

  ### 6. Dify工作流
系统基于Dify构建的工作流是实现智能问答的关键。以下是各组件及其运作方式：
- **开始节点**：以用户输入的`question`作为起始参数，开启工作流。
- **知识检索组件**：在知识库中搜索与问题相关信息，如在生物医学文献和数据中查找线索，为后续处理提供素材。
- **参数提取器（基于deepseek - r1:7b）**：利用该语言模型分析问题，提取关键实体和语义信息，如疾病、基因、化合物名称及关系等，明确问题核心。
- **HTTP请求组件**：向neo4j图形数据库发送POST请求，获取相关知识图谱数据。设置失败重试3次，保障数据获取稳定。
- **变量聚合器**：整合知识检索和HTTP请求组件的结果，统一数据格式，便于后续处理。
- **LLM（deepseek - r1:7b CHAT）组件**：接收整合后信息，运用语言理解和生成能力，结合知识图谱与专业知识，生成回答。
- **结束节点**：输出LLM生成的回答，完成问答流程。

-这套工作流使系统能高效处理用户在Tau蛋白自噬调控通路及阿尔茨海默病研究方面的问题，提供专业解答。

-![cae55fb1d3af40081c2cf75fece4e24](https://github.com/user-attachments/assets/67c812a2-6cd5-4449-8f7e-66bc6ee43f9f)



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
|-----------------------------------|-------------------------------------------------------------------------|
| `requests.exceptions.ConnectionError` | 检查网络连接，添加代理服务器或更换爬取时间                              |
| `selenium.common.exceptions.WebDriverException` | 确认ChromeDriver路径正确，或升级Chrome浏览器                 |
| `Neo4j连接失败`                   | 检查Neo4j服务是否启动，认证信息是否正确                                     |
| `LLM解析结果为空`                 | 调整提示词（prompt），增加示例输入或提高模型温度参数                         |


## 八、联系方式
- 邮箱：m17842059483@163.com
- 项目地址：https://github.com/adddd764/neo4j_knowledgegraph

通过本系统，用户可快速构建Tau蛋白自噬调控通路的知识图谱，支持阿尔茨海默病相关研究的数据整合与可视化分析。如需定制功能或报告问题，请参考上述联系方式。
