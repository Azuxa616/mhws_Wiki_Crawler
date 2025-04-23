import logging
import os
import json
from mhws_crawler import MHWSCrawler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_crawler():
    """测试爬虫功能"""
    logging.info("开始测试爬虫")
    
    # 创建爬虫实例
    crawler = MHWSCrawler()
    
    # 爬取雌火龙数据
    monster_url = "https://mhwilds.kiranico.com/zh/data/monsters/ci-huo-long"
    monster_data = crawler.get_monster_data(monster_url)
    
    if monster_data:
        logging.info(f"成功获取怪物数据: {monster_data['name']}")
        
        # 检查数据完整性
        check_data_integrity(monster_data)
        
        # 保存数据
        crawler.save_monster_data(monster_data, "test_result.json")
        logging.info("测试数据已保存到 test_result.json")
    else:
        logging.error("获取怪物数据失败")

def check_data_integrity(data):
    """检查数据完整性"""
    required_fields = ['name', 'description','base_data', 'hitzone_data', 'status_effects', 'materials']
    
    for field in required_fields:
        if field not in data or not data[field]:
            logging.warning(f"数据字段 '{field}' 为空或不存在")
        else:
            if isinstance(data[field], list):
                logging.info(f"字段 '{field}' 包含 {len(data[field])} 条记录")
            else:
                logging.info(f"字段 '{field}' 数据正常")

if __name__ == "__main__":
    test_crawler()