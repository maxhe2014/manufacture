# Copyright 2016 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from . import models


def mrp_sale_info_post_init_hook(env):
    """
    模块安装后钩子函数：为现有制造订单自动计算销售信息
    处理模块安装前已存在的单据，确保它们能够正确关联销售信息
    
    Odoo 17 版本中，post_init_hook 只接收 env 参数
    """
    # 获取所有制造订单
    mrp_production_model = env['mrp.production']
    all_productions = mrp_production_model.search([])
    
    print(f"开始为 {len(all_productions)} 个制造订单计算销售信息...")
    
    # 批量处理制造订单 - 使用更高效的方式
    batch_size = 100
    for i in range(0, len(all_productions), batch_size):
        batch = all_productions[i:i + batch_size]
        
        # 为每个批次的制造订单查找并设置采购组
        for production in batch:
            # 检查是否已经有 source_procurement_group_id
            if not production.source_procurement_group_id:
                # 方法1：通过成品移动链查找采购组
                procurement_group = production.move_finished_ids.move_dest_ids.group_id[:1]
                
                # 方法2：如果成品移动链没有找到，尝试通过原材料移动链查找
                if not procurement_group:
                    procurement_group = production.move_raw_ids.group_id[:1]
                
                if procurement_group:
                    # 设置 source_procurement_group_id
                    production.write({
                        'source_procurement_group_id': procurement_group.id
                    })
        
        # 强制重新计算当前批次的销售相关字段
        batch._compute_sale_info()
        
        print(f"已处理批次 {i//batch_size + 1}/{(len(all_productions)-1)//batch_size + 1}")
    
    print(f"制造订单数据迁移完成，已处理 {len(all_productions)} 个制造订单")
    
    # 同时处理工单数据
    mrp_workorder_model = env['mrp.workorder']
    all_workorders = mrp_workorder_model.search([])
    
    print(f"开始为 {len(all_workorders)} 个工单计算销售信息...")
    
    # 批量处理工单
    for i in range(0, len(all_workorders), batch_size):
        batch = all_workorders[i:i + batch_size]
        # 强制重新计算工单的销售相关字段
        batch._compute_sale_info()
        
        print(f"已处理工单批次 {i//batch_size + 1}/{(len(all_workorders)-1)//batch_size + 1}")
    
    print(f"工单数据迁移完成，已处理 {len(all_workorders)} 个工单")
    print("数据迁移全部完成！")