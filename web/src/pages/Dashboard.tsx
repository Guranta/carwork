import { PageContainer, StatisticCard } from "@ant-design/pro-components";
import { CarOutlined, FileProtectOutlined, FileTextOutlined, ToolOutlined } from "@ant-design/icons";
import { Col, Row } from "antd";
import { useEffect, useState } from "react";
import { getJSON } from "../api/client";

interface Stats {
  vehicles: number;
  claims: number;
  documents: number;
  orders: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({ vehicles: 0, claims: 0, documents: 0, orders: 0 });

  useEffect(() => {
    Promise.all([
      getJSON<unknown[]>("/vehicles").catch(() => []),
      getJSON<unknown[]>("/claims").catch(() => []),
      getJSON<unknown[]>("/documents").catch(() => []),
      getJSON<unknown[]>("/aftermarket/orders").catch(() => []),
    ]).then(([v, c, d, o]) => {
      setStats({
        vehicles: Array.isArray(v) ? v.length : 0,
        claims: Array.isArray(c) ? c.length : 0,
        documents: Array.isArray(d) ? d.length : 0,
        orders: Array.isArray(o) ? o.length : 0,
      });
    });
  }, []);

  const cards = [
    { title: "车辆档案", value: stats.vehicles, icon: <CarOutlined style={{ fontSize: 28, color: "#1677ff" }} /> },
    { title: "理赔案件", value: stats.claims, icon: <FileProtectOutlined style={{ fontSize: 28, color: "#52c41a" }} /> },
    { title: "单证", value: stats.documents, icon: <FileTextOutlined style={{ fontSize: 28, color: "#faad14" }} /> },
    { title: "维修工单", value: stats.orders, icon: <ToolOutlined style={{ fontSize: 28, color: "#eb2f96" }} /> },
  ];

  return (
    <PageContainer header={{ title: "工作台", breadcrumb: {} }}>
      <Row gutter={[16, 16]}>
        {cards.map((c) => (
          <Col key={c.title} xs={24} sm={12} md={6}>
            <StatisticCard statistic={{ title: c.title, value: c.value, icon: c.icon }} />
          </Col>
        ))}
      </Row>
    </PageContainer>
  );
}
