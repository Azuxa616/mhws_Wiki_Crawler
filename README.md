# 怪物猎人Wilds数据爬虫

这是一个用于抓取 Monster Hunter Wiles 游戏数据的爬虫程序
数据源：https://mhwilds.kiranico.com/

#### 项目地址
Github: https://github.com/Azuxa616/mhws_Wiki_Crawler
Author: @Azuxa616 

## 功能特点

- 自动爬取怪物列表
- 抓取怪物基本信息（名称、描述）
- 抓取怪物弱点数据（部位伤害值）
- 抓取怪物状态异常数据
- 抓取怪物素材掉落信息
- 将数据保存为JSON格式

## 环境要求

- Python 3.6+
- 依赖包：requests, beautifulsoup4

## 安装步骤

1. 克隆或下载本项目到本地
2. 安装依赖包

```bash
pip install -r requirements.txt
```

## 使用方法


```bash
python mhws_crawler.py
```

抓取的数据将保存在项目目录下的`data`文件夹中，文件名为怪物名称。

## 数据格式
#### 怪物列表
抓取的数据将以JSON格式保存，包含以下字段：

- `image`: 怪物图标链接
- `name`: 怪物名称
- `url`: 怪物详情页链接
- `description`: 怪物简单描述

#### 怪物信息
抓取的数据将以JSON格式保存，包含以下字段：

- `name`: 怪物名称
- `description`: 怪物描述
- `weaknesses`:基本数据（种类、生命值、猎人等级经验值）
- `hitzone_data`: 部位伤害数据
- `status_effects`: 状态异常数据
- `materials`: 素材掉落数据


## 注意事项

- 请合理控制爬取频率，避免对目标网站造成过大压力
- 爬取的数据仅供个人学习研究使用，请勿用于商业用途
- 本程序包含错误重试机制，但仍可能因网络问题导致爬取失败