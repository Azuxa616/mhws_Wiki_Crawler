import json
import os
import logging
from monster_parser import MonsterParser
from http_utils import HttpUtils

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MHWSCrawler:
    """魔物猎人Wilds数据爬虫"""
    
    def __init__(self, base_url="https://mhwilds.kiranico.com/zh/data/monsters"):
        """初始化爬虫
        
        Args:
            base_url: 基础URL
        """
        self.base_url = base_url
        
        # 创建HTTP工具类实例
        self.http_utils = HttpUtils(retry_times=3, retry_interval=2, timeout=10)
        
        # 创建数据目录
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _request(self, url):
        """发送HTTP请求并处理可能的异常
        
        Args:
            url: 请求的URL
            
        Returns:
            response: 请求响应
        """
        try:
            # 使用HTTP工具类发送请求
            return self.http_utils.get(url)
        except Exception as e:
            logging.error(f"请求失败: {e}")
            raise
    
    def get_monster_list(self):
        """获取怪物列表

        Returns:
            monster_list: 怪物列表
        """
        logging.info("正在获取怪物列表")

        try:
            # 发送请求获取页面内容
            response = self._request(self.base_url)
            # 使用解析器解析页面内容
            parser = MonsterParser()
            monster_list = parser.parse_monster_list(response.text)

            return monster_list

        except Exception as e:
            logging.error(f"获取怪物列表失败: {e}")
            return []
        
    def get_monster_data(self, monster_url):
        """获取怪物数据
        
        Args:
            monster_url: 怪物页面URL
            
        Returns:
            monster_data: 怪物数据字典
        """
        logging.info(f"正在获取怪物数据: {monster_url}")
        
        try:
            # 发送请求获取页面内容
            response = self._request(monster_url)
            
            # 使用解析器解析页面内容
            parser = MonsterParser()
            monster_data = parser.parse_monster_page(response.text)
            
            return monster_data
            
        except Exception as e:
            logging.error(f"获取怪物数据失败: {e}")
            return None
    
    def save_monster_data(self, monster_data, filename=None):
        """保存怪物数据到JSON文件
        
        Args:
            monster_data: 怪物数据字典
            filename: 文件名，默认为怪物名称
        """
        if not monster_data:
            logging.warning("没有数据可保存")
            return
        
        if not filename:
            filename = f"{monster_data['name']}.json" if monster_data.get('name') else "unknown_monster.json"
        
        file_path = os.path.join(self.data_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(monster_data, f, ensure_ascii=False, indent=2)
            logging.info(f"数据已保存到: {file_path}")
        except Exception as e:
            logging.error(f"保存数据失败: {e}")
    
    def crawl_monster(self, monster_url):
        """爬取单个怪物的数据并保存
        
        Args:
            monster_url: 怪物页面URL
        """
        monster_data = self.get_monster_data(monster_url)
        if monster_data:
            self.save_monster_data(monster_data)

# 主函数
def main():
    # 创建爬虫实例
    crawler = MHWSCrawler()
    
    # 获取怪物列表
    monster_list = crawler.get_monster_list()
    logging.info(f"获取到 {len(monster_list)} 个怪物信息")
    
    # 保存怪物列表数据
    with open(os.path.join(crawler.data_dir, 'monster_list.json'), 'w', encoding='utf-8') as f:
        json.dump(monster_list, f, ensure_ascii=False, indent=2)
    logging.info("怪物列表数据已保存")
    
    # 爬取每个怪物的详细数据
    for monster in monster_list:
        logging.info(f"正在爬取 {monster['name']} 的数据")
        crawler.crawl_monster(f"https://mhwilds.kiranico.com{monster['url']}")
    
    logging.info("所有怪物数据爬取完成")
    logging.info("数据已保存到 data 目录")

if __name__ == "__main__":
    main()