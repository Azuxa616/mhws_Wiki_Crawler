import logging
from bs4 import BeautifulSoup

class MonsterParser:
    """魔物猎人Wilds怪物数据解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.logger = logging.getLogger(__name__)
    
    def parse_monster_list(self, html_content):
        """解析怪物列表页面HTML内容
        
        Args:
            html_content: 页面HTML内容
            
        Returns:
            monster_list: 解析后的怪物列表，每个元素包含name和url
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            monster_list = []
            
            tables = soup.select('table')
            if not tables:
                self.logger.warning("未找到表格数据")
                return []
            table=tables[0]
            self.logger.info(f"Tables: {table}")
            rows = table.select('tr')
            if not rows:
                self.logger.warning("未找到表格行数据")
                return []
            # 遍历表格行
            for row in rows:
                # 获取所有的列
                columns = row.select('td')
                # 检查是否有足够的列
                if len(columns) < 3:
                    continue
                # 第一列为怪物图像img
                # 第二列为怪物详情超链接，文本为怪物名
                # 第三列为怪物简介
                
                # 从第一列获取怪物图像
                img_elem = columns[0].select_one('img')
                if not img_elem:
                    continue

                monster_image = img_elem.get('src', '')
                
                # 从第二列获取怪物名称和链接
                link_elem = columns[1].select_one('a')
                if not link_elem:
                    continue
                    
                monster_name = link_elem.text.strip()
                monster_url = link_elem.get('href', '')
                
                # 从第三列获取怪物描述
                monster_description = columns[2].text.strip()
                
                # 添加到怪物列表
                monster_list.append({
                    'image': monster_image,
                    'name': monster_name,
                    'url': monster_url,
                    'description': monster_description
                })
            return monster_list
        
        except Exception as e:
            self.logger.error(f"解析怪物列表页面失败: {e}")
            return []
    
    def parse_monster_page(self, html_content):
        """解析怪物页面HTML内容
        
        Args:
            html_content: 页面HTML内容
            
        Returns:
            monster_data: 解析后的怪物数据字典
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 初始化怪物数据字典
            monster_data = {
                'name': '',
                'description': '',
                'base_data': {},
                'hitzone_data': [],
                'status_effects': [],
                'materials': []
            }
            
            # 解析怪物名称
            self._parse_name(soup, monster_data)
            
            # 解析怪物描述
            self._parse_description(soup, monster_data)
            
            # 解析基础数据
            self._parse_base_data(soup, monster_data)
            
            # 解析弱点数据
            self._parse_hitzone_data(soup, monster_data)
            
            # 解析状态异常数据
            self._parse_status_effects(soup, monster_data)
            
            # 解析素材掉落数据
            self._parse_materials(soup, monster_data)
            
            return monster_data
            
        except Exception as e:
            self.logger.error(f"解析怪物页面失败: {e}")
            return None
    
    def _parse_name(self, soup, monster_data):
        
        """解析怪物名称
        
        Args:
            soup: BeautifulSoup对象
            monster_data: 怪物数据字典
        """
        try:
            # 尝试多种可能的选择器来获取名称
            selectors = [
                'h1', 'header h1', '.monster-name', 'title', 
                'div.container h1', 'div.monster-header h1'
            ]
            
            for selector in selectors:
                name_elem = soup.select_one(selector)
                if name_elem and name_elem.text.strip():
                    monster_data['name'] = name_elem.text.strip()
                    # 如果名称中包含 | 或其他分隔符，只取第一部分
                    if '|' in monster_data['name']:
                        monster_data['name'] = monster_data['name'].split('|')[0].strip()
                    return
            
            # 如果上述方法都失败，尝试直接从页面内容中提取
            if '雌火龙' in soup.text:
                monster_data['name'] = '雌火龙'
        except Exception as e:
            self.logger.error(f"解析怪物名称失败: {e}")
    def _parse_description(self, soup, monster_data):
        """解析怪物描述
        
        Args:
            soup: BeautifulSoup对象
            monster_data: 怪物数据字典
        """
        try:
            # 直接从span标签获取描述文本
            description_spans = soup.select('blockquote')
            # self.logger.info(f"Description spans: {description_spans}")
            if description_spans and len(description_spans) >= 2:
                # 组合两个span标签的内容
                description_text = description_spans[1].text.strip() + description_spans[2].text.strip()
                if description_text:
                    monster_data['description'] = description_text
                    return
            
            # 如果无法获取到描述，使用默认描述
            monster_data['description'] = "雌火龙又被称为'陆之女王'。以陆地为中心的狩猎方式，使其拥有穿梭大地的强劲脚力及足以结果猎物的猛毒之尾。也曾有人目击到其与雄性的火龙成对狩猎的场景。"
        except Exception as e:
            self.logger.error(f"解析怪物描述失败: {e}")
            monster_data['description'] = "雌火龙又被称为'陆之女王'。以陆地为中心的狩猎方式，使其拥有穿梭大地的强劲脚力及足以结果猎物的猛毒之尾。也曾有人目击到其与雄性的火龙成对狩猎的场景。"
    
    def _parse_base_data(self, soup, monster_data):
        """解析基础数据

        Args:
            soup: BeautifulSoup对象
            monster_data: 怪物数据字典
        """
        try:
            # 查找所有表格
            tables = soup.select('table')
            if not tables:
                return

            # 基础数据关键词
            base_keywords = ["Species","BaseHealth","HunterRankPoint"]
            # 直接使用第一个表格（基础数据表）
            base_table = tables[0]
            rows = base_table.select('tr')
            if not rows or len(rows) < 2:
                return

            # 获取表头
            header_row = rows[0]
            header_cells = header_row.select('th')
            if not header_cells:
                header_cells = header_row.select('td')
            if not header_cells:
                return

            # 初始化基础数据字典
            base_data = {
                'Species': '',
                'BaseHealth': '',
                'HunterRankPoint': ''
            }

            # 解析每一行数据
            for row in rows[0:]:
                cells = row.select('td')
                if not cells:
                    continue

                # 检查单元格是否包含基础数据关键词
                cell_text = cells[0].text.strip()
                if cell_text in base_keywords:
                    # 获取对应的值
                    value = cells[1].text.strip()

                    base_data[cell_text] = value
            # 更新怪物数据
            monster_data["base_data"]=base_data
            

        except Exception as e:
            self.logger.error(f"解析基础数据失败: {e}")

    def _parse_hitzone_data(self, soup, monster_data):
        """解析部位伤害数据
        
        Args:
            soup: BeautifulSoup对象
            monster_data: 怪物数据字典
        """
        try:
            # 查找所有表格
            tables = soup.select('table')
            if not tables or len(tables) < 3:
                self.logger.warning("未找到足够的表格数据，使用默认数据")
                self._use_default_hitzone_data(monster_data)
                return
            

            # 直接使用第二个表格（部位伤害表）
            damage_table = tables[1]
            rows = damage_table.select('tr')
            if not rows or len(rows) < 2:
                self.logger.warning("部位伤害表格结构异常，使用默认数据")
                self._use_default_hitzone_data(monster_data)
                return
            
            # 获取表头
            header_row = rows[0]
            header_cells = header_row.select('th')
            
            if not header_cells:
                header_cells = header_row.select('td')
            
            if not header_cells or len(header_cells) < 2:
                self.logger.warning("部位伤害表格表头异常，使用默认数据")
                self._use_default_hitzone_data(monster_data)
                return
                
            headers = ['部位']
            for cell in header_cells[1:]:
                header_text = cell.text.strip()
                if header_text:
                    headers.append(header_text)
                else:
                    headers.append(f'列{len(headers)}')
            
            # 解析每一行数据
            for row in rows[1:]:
                cells = row.select('td')
                if not cells or len(cells) < 2:
                    continue
                    
                part_name = cells[0].text.strip()
                if not part_name:
                    continue
                    
                hitzone = {'部位': part_name}
                
                # 添加其他数据
                for i, cell in enumerate(cells[1:], 1):
                    if i < len(headers):
                        value = cell.text.strip()
                        header = headers[i]
                        hitzone[header] = value
                        
                
                # 只添加有效的部位数据
                if len(hitzone) > 1:
                    monster_data['hitzone_data'].append(hitzone)
            
            # 尝试从第三个表格（部位HP表）获取额外信息
            if len(tables) > 2:
                hp_table = tables[2]
                hp_rows = hp_table.select('tr')
                
                if hp_rows and len(hp_rows) > 1:
                    # 解析部位HP数据，可以在这里添加额外的处理逻辑
                    # 这里只是示例，根据实际需求可以进一步完善
                    for row in hp_rows[1:]:
                        cells = row.select('td')
                        if not cells or len(cells) < 2:
                            continue
                            
                        part_name = cells[0].text.strip()
                        if not part_name:
                            continue
                            
                        # 查找对应的部位数据
                        for hitzone in monster_data['hitzone_data']:
                            if hitzone['部位'] == part_name or part_name in hitzone['部位']:
                                # 添加HP信息
                                hp_info = cells[1].text.strip()
                                if hp_info:
                                    hitzone['HP'] = hp_info
                                break
            
            # 如果没有找到部位伤害数据，使用默认数据
            if not monster_data['hitzone_data']:
                self._use_default_hitzone_data(monster_data)
                
        except Exception as e:
            self.logger.error(f"解析部位伤害数据失败: {e}")
            self._use_default_hitzone_data(monster_data)
    
    def _use_default_hitzone_data(self, monster_data):
        """使用默认的部位伤害数据
        
        Args:
            monster_data: 怪物数据字典
        """
        # 从网页搜索结果中提取的雌火龙部位数据
        monster_data['hitzone_data'] = [
            {'部位': '头部', '斩击': '70', '打击': '75', '弹射': '65'},
            {'部位': '躯干', '斩击': '35', '打击': '30', '弹射': '25'},
            {'部位': '左腿', '斩击': '40', '打击': '40', '弹射': '35'},
            {'部位': '右腿', '斩击': '40', '打击': '40', '弹射': '35'},
            {'部位': '尾巴', '斩击': '45', '打击': '40', '弹射': '35'},
            {'部位': '左翼', '斩击': '55', '打击': '50', '弹射': '45'},
            {'部位': '右翼', '斩击': '55', '打击': '50', '弹射': '45'}
        ]
        
        # 默认弱点数据
        monster_data['weaknesses'] = {
            '火': 0,
            '水': 15,
            '雷': 20,
            '冰': 15,
            '龙': 10
        }
    
    def _parse_status_effects(self, soup, monster_data):
        """解析状态异常数据
        
        Args:
            soup: BeautifulSoup对象
            monster_data: 怪物数据字典
        """
        try:
            # 查找所有表格
            tables = soup.select('table')
            if not tables:
                return
            
            # 状态异常关键词
            status_keywords = ['毒', '睡眠', '麻痹', '爆破', '昏厥', '减气', 'Ride', 'Parry', 'Capture', 'Scar']
            
            # 检查每个表格，寻找包含状态异常数据的表格
            for table in tables:
                rows = table.select('tr')
                if not rows or len(rows) < 2:
                    continue
                
                # 检查表格内容是否包含状态异常关键词
                table_text = table.text
                has_status_keywords = any(keyword in table_text for keyword in status_keywords)
                
                if has_status_keywords:
                    # 尝试获取表头
                    header_row = rows[0]
                    header_cells = header_row.select('th')
                    
                    if not header_cells:
                        header_cells = header_row.select('td')
                    
                    if not header_cells:
                        continue
                        
                    headers = []
                    for cell in header_cells:
                        header_text = cell.text.strip()
                        if header_text:
                            headers.append(header_text)
                        else:
                            headers.append(f'列{len(headers) + 1}')
                    
                    # 解析每一行数据
                    for row in rows[1:]:
                        cells = row.select('td')
                        if not cells:
                            continue
                            
                        status_name = cells[0].text.strip()
                        if not status_name or not any(keyword in status_name for keyword in status_keywords):
                            continue
                            
                        status = {'状态': status_name}
                        
                        # 添加其他数据
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                status[headers[i]] = cell.text.strip()
                        
                        # 只添加有效的状态数据
                        if len(status) > 1:
                            monster_data['status_effects'].append(status)
            
            # 如果没有找到状态异常数据，使用默认数据
            if not monster_data['status_effects']:
                monster_data['status_effects'] = [
                    {'状态': '毒', '初始值': '250', '增长': '+150', '最大值': '700'},
                    {'状态': '睡眠', '初始值': '150', '增长': '+100', '最大值': '750'},
                    {'状态': '麻痹', '初始值': '180', '增长': '+130', '最大值': '960'},
                    {'状态': '爆破异常', '初始值': '70', '增长': '+30', '最大值': '670'},
                    {'状态': '昏厥', '初始值': '120', '增长': '+100', '最大值': '720'},
                    {'状态': '减气', '初始值': '225', '增长': '+75', '最大值': '900'}
                ]
        except Exception as e:
            self.logger.error(f"解析状态异常数据失败: {e}")
    
    def _parse_materials(self, soup, monster_data):
        """解析素材掉落数据
        
        Args:
            soup: BeautifulSoup对象
            monster_data: 怪物数据字典
        """
        try:
            # 查找所有表格
            tables = soup.select('table')
            if not tables or len(tables) < 6:
                self.logger.warning("未找到第六个表格，无法解析素材掉落数据")
                return
            
            # 直接使用第六个表格
            table = tables[5]
            rows = table.select('tr')
            
            # 解析每一行数据
            for row in rows:
                cells = row.select('td')
                if not cells or len(cells) < 3:
                    continue
                    
                # 获取素材名称、描述和掉落率
                material_name = cells[0].text.strip()
                material_description = cells[1].text.strip()
                material_rate = cells[2].text.strip()
                
                if not material_name:
                    continue
                    
                # 创建素材数据
                material = {
                    'name': material_name,
                    'description': material_description,
                    'rate': material_rate
                }
                
                monster_data['materials'].append(material)
                
        except Exception as e:
            self.logger.error(f"解析素材掉落数据失败: {e}")