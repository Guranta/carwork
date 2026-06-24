"""policy + repair_shop tables and seed data

Revision ID: 0002_policies_shops
Revises: 0001_initial
Create Date: 2026-06-25

"""

from alembic import op

revision = "0002_policies_shops"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from app.db.base import Base
    from app.models.policy import Policy
    from app.models.repair_shop import RepairShop

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, tables=[Policy.__table__, RepairShop.__table__])

    op.bulk_insert(Policy.__table__, _POLICIES)
    op.bulk_insert(RepairShop.__table__, _SHOPS)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS repair_shop")
    op.execute("DROP TABLE IF EXISTS policy")


# ---- seed: 保单（贴近真实，便于演示报销价理算）----
_POLICIES = [
    {
        "policy_no": "PA2026BJ0001234",
        "insured_name": "张明",
        "insured_phone": "13800001234",
        "plate_no": "京A12345",
        "vin": "LFV2A21K9X3001234",
        "insurance_company": "人保财险",
        "coverage_types": ["交强险", "车辆损失险", "第三者责任险", "不计免赔"],
        "deductible": 0,
        "payout_ratio": 1.0,
        "sum_insured": 158000,
        "effective_from": "2026-01-01",
        "effective_to": "2026-12-31",
        "status": "active",
        "active": True,
    },
    {
        "policy_no": "PA2026SH0005678",
        "insured_name": "李娜",
        "insured_phone": "13800005678",
        "plate_no": "沪B88888",
        "vin": "LBVHS7AN0N3005678",
        "insurance_company": "平安产险",
        "coverage_types": ["交强险", "车辆损失险", "不计免赔"],
        "deductible": 500,
        "payout_ratio": 0.85,
        "sum_insured": 220000,
        "effective_from": "2026-03-15",
        "effective_to": "2027-03-14",
        "status": "active",
        "active": True,
    },
    {
        "policy_no": "PA2025GD0009012",
        "insured_name": "王强",
        "insured_phone": "13800009012",
        "plate_no": "粤A66666",
        "vin": "LVSHFFAC3HF3009012",
        "insurance_company": "太平洋产险",
        "coverage_types": ["交强险", "第三者责任险"],
        "deductible": 0,
        "payout_ratio": 1.0,
        "sum_insured": None,
        "effective_from": "2025-09-01",
        "effective_to": "2026-08-31",
        "status": "active",
        "active": True,
    },
]


# ---- seed: 合作修理厂（含经纬度，演示"最近修理厂"）----
_SHOPS = [
    {
        "name": "途虎养车·徐汇旗舰店",
        "address": "上海市徐汇区漕溪北路 888 号",
        "phone": "021-64120001",
        "city": "上海",
        "lat": 31.1942,
        "lng": 121.4366,
        "labor_rate": 120,
        "is_partner": True,
        "brands": ["大众", "丰田", "本田", "别克"],
        "rating": 4.7,
    },
    {
        "name": "上汽大众·浦东特约维修站",
        "address": "上海市浦东新区张杨路 2888 号",
        "phone": "021-58880002",
        "city": "上海",
        "lat": 31.2304,
        "lng": 121.5256,
        "labor_rate": 150,
        "is_partner": True,
        "brands": ["大众", "斯柯达", "奥迪"],
        "rating": 4.8,
    },
    {
        "name": "车享家·闵行莘庄店",
        "address": "上海市闵行区莘庄镇都市路 5001 号",
        "phone": "021-54970003",
        "city": "上海",
        "lat": 31.1138,
        "lng": 121.3855,
        "labor_rate": 100,
        "is_partner": True,
        "brands": ["通用", "福特", "日产"],
        "rating": 4.5,
    },
    {
        "name": "博世车联·北京朝阳店",
        "address": "北京市朝阳区建国路 88 号",
        "phone": "010-85780001",
        "city": "北京",
        "lat": 39.9087,
        "lng": 116.4636,
        "labor_rate": 140,
        "is_partner": True,
        "brands": ["奔驰", "宝马", "奥迪", "大众"],
        "rating": 4.6,
    },
    {
        "name": "途虎养车·北京海淀店",
        "address": "北京市海淀区中关村大街 30 号",
        "phone": "010-62550002",
        "city": "北京",
        "lat": 39.9847,
        "lng": 116.3186,
        "labor_rate": 120,
        "is_partner": True,
        "brands": ["丰田", "本田", "比亚迪", "特斯拉"],
        "rating": 4.7,
    },
]
