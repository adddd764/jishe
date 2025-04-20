# coding: utf-8
import os
import json
from py2neo import Graph, Node


class PathwayGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/data.json')  # 替换为实际JSON文件路径
        self.g = Graph("bolt://localhost:7687", auth=("neo4j", "neo4j12345"))  # 连接Neo4j

    '''读取节点和关系'''

    def read_nodes_and_rels(self):
        compounds = []  # 调控化合物（包括各类药物）
        genes = []  # 基因（核心基因、调控基因等）
        pathways = []  # 信号通路
        diseases = []  # 疾病
        proteins = []  # 蛋白质
        methods = []  # 实验方法（模型、细胞等）
        enzymes = []  # 酶（激酶、磷酸酶等）

        rels_target = []  # 化合物 - 靶点关系（Compound - Gene/Protein）
        rels_pathway = []  # 节点 - 信号通路关系（Entity - Pathway）
        rels_disease = []  # 节点 - 疾病关系
        rels_enzyme = []  # 酶 - 调控关系

        for data in open(self.data_path, encoding='utf8'):
            data_json = json.loads(data)
            node_type = data_json.get('type', '')
            related_pathway = data_json.get('related_pathway', '')

            # 处理化合物（扩展类型包括他汀类、抑制剂等）
            if node_type in ['调控化合物', '他汀类药物', '自噬增强剂', 'MTOR抑制剂',
                             'FKBP5抑制剂', '天然化合物', '卤胺化合物', '神经肽',
                             '解偶联剂', '自噬诱导剂', 'GSK3β抑制剂', 'V-ATPase抑制剂']:
                compound_name = data_json['name']
                compounds.append(compound_name)
                # 处理靶点关系
                target = data_json.get('target', '')
                if target:
                    rels_target.append([compound_name, target])
                # 处理通路关系
                if related_pathway:
                    rels_pathway.append([compound_name, related_pathway])

            # 处理基因（核心基因、调控基因、转录因子等）
            elif node_type in ['核心基因', '调控基因', '自噬调控基因', '基因突变',
                               '转录因子', '自噬调控基因', '溶酶体调控基因']:
                gene_name = data_json['name']
                genes.append(gene_name)
                if related_pathway:
                    rels_pathway.append([gene_name, related_pathway])
                # 提取疾病关联
                self.extract_diseases(data_json, gene_name, rels_disease)

            # 处理蛋白质（带uniprot_id或明确蛋白质类型）
            elif 'uniprot_id' in data_json or node_type in ['溶酶体蛋白', '分子马达蛋白', '小GTP酶',
                                                            '分子伴侣', '突触后蛋白', '凋亡标志物',
                                                            'ESCRT-III复合体亚基', '组蛋白乙酰化抑制因子',
                                                            '线粒体分裂蛋白', 'E3泛素连接酶', '线粒体外膜受体',
                                                            '促凋亡蛋白', '线粒体运输调控蛋白', '去乙酰化酶',
                                                            '磷脂翻转酶', '炎症因子', '溶酶体酶', '自噬受体',
                                                            '衔接蛋白', '自噬标记物']:
                protein_name = data_json['name']
                proteins.append(protein_name)
                if related_pathway:
                    rels_pathway.append([protein_name, related_pathway])
                # 提取疾病关联
                self.extract_diseases(data_json, protein_name, rels_disease)

            # 处理实验方法（模型、细胞等）
            elif node_type in ['动物模型', '细胞模型']:
                method_name = data_json['name']
                methods.append(method_name)
                # 实验方法可能没有通路，跳过通路处理

            # 处理疾病（从related_diseases提取）
            if 'related_diseases' in data_json:
                for disease in data_json['related_diseases']:
                    diseases.append(disease)

            # 处理酶（从modifications或type中提取）
            if 'modifications' in data_json:
                for mod in data_json['modifications']:
                    if 'enzyme' in mod:
                        enzymes.append(mod['enzyme'])
            if node_type in ['激酶', '磷酸酶', 'E3泛素连接酶']:
                enzymes.append(data_json['name'])

        # 去重处理
        return (
            set(compounds), set(genes), set(pathways), set(diseases),
            set(proteins), set(methods), set(enzymes),
            rels_target, rels_pathway, rels_disease, rels_enzyme
        )

    '''辅助方法：提取疾病关联'''

    def extract_diseases(self, data_json, entity_name, rels_disease):
        if 'related_diseases' in data_json:
            for disease in data_json['related_diseases']:
                rels_disease.append([entity_name, disease])

    '''创建节点'''

    def create_node(self, label, nodes, properties=None):
        """创建节点，支持自定义属性"""
        count = 0
        for node_name in nodes:
            node_props = {'name': node_name}
            if properties:
                node_props.update(properties)

            # 处理复杂属性（转为JSON字符串）
            for k, v in list(node_props.items()):
                if isinstance(v, (dict, list)):
                    node_props[k] = json.dumps(v)

            node = Node(label, **node_props)
            try:
                self.g.create(node)
                count += 1
                print(f"创建{label}节点：{node_name}，累计{count}个")
            except Exception as e:
                print(f"创建{label}节点失败：{node_name}，错误：{e}")
        return

    '''创建知识图谱'''

    def build_knowledge_graph(self):
        # 读取节点和关系
        (compounds, genes, pathways, diseases, proteins, methods, enzymes,
         rels_target, rels_pathway, rels_disease, rels_enzyme) = self.read_nodes_and_rels()

        # 创建节点
        self.create_node("Compound", compounds)
        self.create_node("Gene", genes)
        self.create_node("Pathway", pathways)
        self.create_node("Disease", diseases)
        self.create_node("Protein", proteins)
        self.create_node("Method", methods)
        self.create_node("Enzyme", enzymes)

        # 创建关系：化合物 - 靶点（基因/蛋白质）
        self.create_relationship("Compound", "Gene", rels_target, "targets", "作用靶点")
        self.create_relationship("Compound", "Protein", rels_target, "targets", "作用靶点")

        # 创建关系：节点 - 信号通路
        self.create_relationship("Compound", "Pathway", rels_pathway, "involved_in", "参与")
        self.create_relationship("Gene", "Pathway", rels_pathway, "involved_in", "参与")
        self.create_relationship("Protein", "Pathway", rels_pathway, "involved_in", "参与")

        # 创建关系：节点 - 疾病
        self.create_relationship("Gene", "Disease", rels_disease, "assoc_with", "关联疾病")
        self.create_relationship("Protein", "Disease", rels_disease, "assoc_with", "关联疾病")
        self.create_relationship("Compound", "Disease", rels_disease, "treats", "治疗")  # 可选关系

    '''创建关系边'''

    def create_relationship(self, start_label, end_label, edges, rel_type, rel_name):
        """创建关系边（带去重处理）"""
        count = 0
        unique_edges = set(f"{s}###{e}" for s, e in edges if e)  # 过滤空终点

        for edge in unique_edges:
            s, e = edge.split('###')
            query = (
                f"MATCH (p:{start_label} {{name:'{s}'}}), (q:{end_label} {{name:'{e}'}}) "
                f"CREATE (p)-[rel:{rel_type} {{name:'{rel_name}'}}]->(q)"
            )
            try:
                self.g.run(query)
                count += 1
                print(f"创建{rel_type}关系：{s} -> {e}，累计{count}条")
            except Exception as e:
                print(f"创建{rel_type}关系失败：{s} -> {e}，错误：{e}")
        return


if __name__ == "__main__":
    handler = PathwayGraph()
    print("开始搭建知识图谱...")
    handler.build_knowledge_graph()
    print("知识图谱搭建完成！")
