import os
import requests
from bs4 import BeautifulSoup
from Bio import Entrez
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options



# 定义保存文献的文件夹
output_folder = "medical_doc"
os.makedirs(output_folder, exist_ok=True)

def search_pubmed(query, retmax=10):
    """
    在PubMed上搜索文献
    :param query: 搜索查询词
    :param retmax: 返回的最大文献数量
    :return: 文献ID列表
    """
    handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]

def fetch_pubmed_pdfs(id_list):
    """
    根据文献ID列表尝试从PubMed获取PDF文献
    :param id_list: 文献ID列表
    """
    for pmid in id_list:
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_links = soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))
        for link in pdf_links:
            pdf_url = link['href']
            if not pdf_url.startswith('http'):
                pdf_url = f"https://pubmed.ncbi.nlm.nih.gov{pdf_url}"
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                with open(os.path.join(output_folder, f"{pmid}.pdf"), 'wb') as f:
                    f.write(pdf_response.content)
                print(f"已下载PubMed文献 {pmid}.pdf")

def search_sciencedirect(query, retmax=10):
    """
    在ScienceDirect上搜索文献
    :param query: 搜索查询词
    :param retmax: 返回的最大文献数量
    """
    base_url = "https://www.sciencedirect.com/search"
    params = {
        "qs": query,
        "show": retmax
    }
    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_links = soup.find_all('a', class_='result-list-title-link')
    for link in article_links:
        article_url = f"https://www.sciencedirect.com{link['href']}"
        try:
            # 设置Chrome浏览器选项
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            service = Service('path/to/chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(article_url)
            pdf_button = driver.find_element(By.CSS_SELECTOR, 'a.pdf-download-link')
            pdf_url = pdf_button.get_attribute('href')
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                article_id = article_url.split('/')[-1]
                with open(os.path.join(output_folder, f"{article_id}.pdf"), 'wb') as f:
                    f.write(pdf_response.content)
                print(f"已下载ScienceDirect文献 {article_id}.pdf")
            driver.quit()
        except Exception as e:
            print(f"下载ScienceDirect文献失败: {e}")

def search_ieee(query, retmax=10):
    """
    在IEEE Xplore上搜索文献
    :param query: 搜索查询词
    :param retmax: 返回的最大文献数量
    """
    base_url = "https://ieeexplore.ieee.org/search/searchresult.jsp"
    params = {
        "queryText": query,
        "rowsPerPage": retmax
    }
    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_links = soup.find_all('a', class_='document-title')
    for link in article_links:
        article_url = f"https://ieeexplore.ieee.org{link['href']}"
        try:
            # 设置Chrome浏览器选项
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            service = Service('path/to/chromedriver')  # 替换为你的ChromeDriver路径
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(article_url)
            pdf_button = driver.find_element(By.CSS_SELECTOR, 'a.art-pdf-link')
            pdf_url = pdf_button.get_attribute('href')
            if not pdf_url.startswith('http'):
                pdf_url = f"https://ieeexplore.ieee.org{pdf_url}"
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                article_id = article_url.split('/')[-1].split('?')[0]
                with open(os.path.join(output_folder, f"{article_id}.pdf"), 'wb') as f:
                    f.write(pdf_response.content)
                print(f"已下载IEEE Xplore文献 {article_id}.pdf")
            driver.quit()
        except Exception as e:
            print(f"下载IEEE Xplore文献失败: {e}")

if __name__ == "__main__":
    query = "Alzheimer’s Disease; Autophagy; Tau Protein"  # 关键词
    retmax = 5  #需要爬取的文献数量

    # 从PubMed搜索并下载文献
    pubmed_id_list = search_pubmed(query, retmax)
    fetch_pubmed_pdfs(pubmed_id_list)

    # 从ScienceDirect搜索并下载文献
    search_sciencedirect(query, retmax)

    # 从IEEE Xplore搜索并下载文献
    search_ieee(query, retmax)

    # 调用data clean.py中的函数处理下载的PDF文件
    from data_clean import process_all_pdfs
    process_all_pdfs(output_folder)