import fitz
import re
import nltk
import os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Spacer

# 下载必要的 nltk 数据
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def extract_text_from_pdf(pdf_path):
    """从 PDF 文件中提取文本内容，过滤非文字部分"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        # 遍历页面上的文本块
        for block in page.get_text("blocks"):
            if block[6] == 0:  # 只处理文本块（类型为 0）
                text += block[4]
    return text


def remove_header_footer(text):
    """去除页眉页脚"""
    # 假设页眉页脚包含页码，通过正则匹配去除
    text = re.sub(r'(\d+)\s*$', '', text, flags=re.MULTILINE)
    return text


def remove_references(text):
    """去除参考文献部分"""
    # 假设参考文献以 "References" 开头
    if "References" in text:
        text = text.split("References")[0]
    return text


def clean_text(text):
    """清洗文本，去除特殊字符、多余空格，转换为小写"""
    # 去除特殊字符，只保留字母、数字、空格、关键标点符号
    cleaned_text = re.sub(r'[^\w\s.,!?]', '', text)
    # 去除多余的空格，但保留换行符
    cleaned_text = re.sub(r'[^\S\n]+', ' ', cleaned_text).strip()
    # 转换为小写
    cleaned_text = cleaned_text.lower()
    return cleaned_text


def split_sentences(text):
    """将文本分割成句子"""
    sentences = sent_tokenize(text)
    return sentences


def remove_stopwords(sentences):
    """去除句子中的停用词"""
    stop_words = set(stopwords.words('english'))
    filtered_sentences = []
    for sentence in sentences:
        words = sentence.split()
        filtered_words = [word for word in words if word not in stop_words]
        filtered_sentence = " ".join(filtered_words)
        filtered_sentences.append(filtered_sentence)
    return filtered_sentences


def lemmatize_sentences(sentences):
    """对句子中的单词进行词形还原"""
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentences = []
    for sentence in sentences:
        words = word_tokenize(sentence)
        lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
        lemmatized_sentence = " ".join(lemmatized_words)
        lemmatized_sentences.append(lemmatized_sentence)
    return lemmatized_sentences


def save_cleaned_text_to_pdf(sentences, output_path):
    """将清洗后的文本保存到 PDF 文档中"""
    c = canvas.Canvas(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    title_style = styles['Heading1']

    # 添加标题
    title = Paragraph('清洗后的医学文献内容', title_style)
    w, h = title.wrapOn(c, letter[0] - 100, letter[1] - 100)
    title.drawOn(c, 50, letter[1] - 50 - h)

    # 添加段落说明
    intro = Paragraph('以下是从 PDF 中提取并清洗后的文本内容：', normal_style)
    w, h = intro.wrapOn(c, letter[0] - 100, letter[1] - 200)
    intro.drawOn(c, 50, letter[1] - 120 - h)

    y_position = letter[1] - 200
    for sentence in sentences:
        p = Paragraph(sentence, normal_style)
        w, h = p.wrapOn(c, letter[0] - 100, y_position)
        if y_position - h < 50:
            c.showPage()
            y_position = letter[1] - 50
        p.drawOn(c, 50, y_position - h)
        y_position -= h + 20

    c.save()


def process_all_pdfs(folder_path):
    """处理指定文件夹中的所有 PDF 文件，并保存到清洗后文件夹"""
    # 创建清洗后文件夹（英文名称）
    output_folder = "medical_doc_cleaned"
    os.makedirs(output_folder, exist_ok=True)  # 自动创建，存在则忽略

    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            # 生成清洗后文件路径（保存在 medical_doc_cleaned 文件夹）
            output_path = os.path.join(output_folder, f'cleaned_{filename}')

            # 提取文本
            extracted_text = extract_text_from_pdf(pdf_path)
            # 去除页眉页脚
            text_without_header_footer = remove_header_footer(extracted_text)
            # 去除参考文献
            text_without_references = remove_references(text_without_header_footer)
            # 清洗文本
            cleaned_text = clean_text(text_without_references)
            # 分割句子
            sentences = split_sentences(cleaned_text)
            # 去除停用词
            filtered_sentences = remove_stopwords(sentences)
            # 词形还原
            lemmatized_sentences = lemmatize_sentences(filtered_sentences)
            # 保存清洗后的文本到 PDF 文档
            save_cleaned_text_to_pdf(lemmatized_sentences, output_path)
            print(f'已处理 {filename}，保存到 {output_path}')


if __name__ == "__main__":
    folder_path = "medical_doc"  # 原始文件夹路径
    process_all_pdfs(folder_path)