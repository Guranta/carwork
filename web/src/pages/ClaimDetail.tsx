import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { PageContainer, ProCard, ProDescriptions } from "@ant-design/pro-components";
import { Alert, Button, Empty, Input, message, Space, Table, Tag, Typography } from "antd";
import { CameraOutlined, MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { getJSON, postJSON } from "../api/client";

interface Damage {
  part?: string;
  type?: string;
  severity?: string;
  repair?: string;
  estimate?: number;
}
interface Assessment {
  damages?: Damage[];
  summary?: string;
  total_estimate?: number;
  confidence?: number;
}

export default function ClaimDetail() {
  const { id } = useParams<{ id: string }>();
  const [claim, setClaim] = useState<Record<string, unknown> | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [images, setImages] = useState<string[]>([""]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    getJSON<Record<string, unknown>>(`/claims/${id}`)
      .then((data) => {
        setClaim(data);
        if (data?.loss_assessment) setAssessment(data.loss_assessment as Assessment);
      })
      .catch(() => {});
  }, [id]);

  const runAssess = async () => {
    const urls = images.map((i) => i.trim()).filter(Boolean);
    if (urls.length === 0) {
      message.warning("请至少填写一张损伤照片 URL");
      return;
    }
    setLoading(true);
    try {
      const { assessment: a } = await postJSON<{ assessment: Assessment }>(
        `/claims/${id}/assess-damage`,
        { image_urls: urls }
      );
      setAssessment(a);
      message.success("定损完成");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer header={{ title: `理赔案 ${claim?.case_no || ""}`, breadcrumb: {} }} onBack={() => history.back()}>
      <ProCard title="案件信息" headerBordered style={{ marginBottom: 16 }}>
        <ProDescriptions column={2} dataSource={claim || {}}>
          <ProDescriptions.Item label="案件号" dataIndex="case_no" />
          <ProDescriptions.Item label="状态" dataIndex="status" />
          <ProDescriptions.Item label="阶段" dataIndex="stage" />
          <ProDescriptions.Item label="预估金额" dataIndex="estimated_amount" valueType="money" />
        </ProDescriptions>
      </ProCard>

      <ProCard
        title={<span><CameraOutlined /> AI 视觉定损</span>}
        headerBordered
        style={{ marginBottom: 16 }}
      >
        <div style={{ marginBottom: 8 }}>
          <Typography.Text strong>车辆损伤照片 URL</Typography.Text>
        </div>
        {images.map((url, idx) => (
          <Space key={idx} style={{ display: "flex", marginBottom: 8 }} align="center">
            <Input
              placeholder="https://example.com/damage1.jpg"
              value={url}
              style={{ width: 520 }}
              onChange={(e) => setImages((prev) => prev.map((v, i) => (i === idx ? e.target.value : v)))}
            />
            {images.length > 1 && (
              <MinusCircleOutlined
                onClick={() => setImages((prev) => prev.filter((_, i) => i !== idx))}
              />
            )}
          </Space>
        ))}
        <Button type="dashed" icon={<PlusOutlined />} onClick={() => setImages((prev) => [...prev, ""])}>
          添加照片
        </Button>
        <div style={{ marginTop: 12 }}>
          <Button type="primary" loading={loading} onClick={runAssess}>
            开始 AI 定损
          </Button>
          <Typography.Text type="secondary" style={{ marginLeft: 12 }}>
            需后端配置视觉模型 Key（如 DASHSCOPE_API_KEY）
          </Typography.Text>
        </div>
      </ProCard>

      {assessment && (
        <ProCard title="定损结果" headerBordered>
          {typeof assessment.confidence === "number" && assessment.confidence < 0.7 && (
            <Alert
              style={{ marginBottom: 12 }}
              type="warning"
              showIcon
              message={`置信度较低（${assessment.confidence}），建议转人工定损员复核`}
            />
          )}
          <div style={{ marginBottom: 12 }}>
            概述：{assessment.summary || "—"} ｜ 预估总额：
            <b style={{ color: "#cf1322" }}>¥ {assessment.total_estimate ?? "—"}</b> ｜ 置信度：
            <Tag color={assessment.confidence != null && assessment.confidence >= 0.7 ? "green" : "orange"}>
              {assessment.confidence ?? "—"}
            </Tag>
          </div>
          {assessment.damages?.length ? (
            <Table
              rowKey={(_, i) => String(i)}
              size="small"
              pagination={false}
              dataSource={assessment.damages}
              columns={[
                { title: "部位", dataIndex: "part" },
                { title: "损伤类型", dataIndex: "type" },
                { title: "严重程度", dataIndex: "severity" },
                { title: "维修方式", dataIndex: "repair" },
                { title: "估价", dataIndex: "estimate", render: (v) => (v != null ? `¥ ${v}` : "—") },
              ]}
            />
          ) : (
            <Empty description="无损伤明细" />
          )}
        </ProCard>
      )}
    </PageContainer>
  );
}
