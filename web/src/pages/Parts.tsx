import { useState } from "react";
import { PageContainer, ProCard, ProForm, ProFormText } from "@ant-design/pro-components";
import { Button, Empty, Spin, Tag, Typography, message } from "antd";
import { CopyOutlined } from "@ant-design/icons";
import { postJSON } from "../api/client";

interface PartItem {
  name?: string;
  oe_hint?: string;
  alternatives?: string[];
}
interface PartsAnswer {
  parts?: PartItem[];
  notes?: string;
}

export default function Parts() {
  const [loading, setLoading] = useState(false);
  const [parsed, setParsed] = useState<PartsAnswer | null>(null);
  const [raw, setRaw] = useState("");

  const onSubmit = async (vals: { query: string; vin?: string }) => {
    setLoading(true);
    setParsed(null);
    setRaw("");
    try {
      const { answer } = await postJSON<{ answer: string }>(`/aftermarket/parts/match`, {
        query: vals.query,
        vin: vals.vin,
      });
      setRaw(answer);
      try {
        setParsed(JSON.parse(answer));
      } catch {
        setParsed(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const copy = (text: string) => {
    navigator.clipboard?.writeText(text).then(
      () => message.success("已复制"),
      () => message.error("复制失败")
    );
  };

  return (
    <PageContainer header={{ title: "配件匹配", breadcrumb: {} }}>
      <ProCard headerBordered>
        <ProForm<{ query: string; vin?: string }> onFinish={onSubmit} submitter={{ searchConfig: { submitText: "AI 匹配" } }}>
          <ProFormText name="vin" label="车架号 VIN（可选）" placeholder="用于精确匹配车型" />
          <ProFormText
            name="query"
            label="配件需求"
            placeholder="如：前保险杠、左前大灯、刹车片"
            rules={[{ required: true }]}
          />
        </ProForm>
      </ProCard>

      <ProCard title="匹配结果" headerBordered style={{ marginTop: 16 }}>
        {loading ? (
          <div style={{ textAlign: "center", padding: 32 }}>
            <Spin tip="AI 匹配中…" />
          </div>
        ) : parsed && parsed.parts?.length ? (
          <>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {parsed.parts.map((p, i) => (
                <div
                  key={i}
                  style={{
                    border: "1px solid #f0f0f0",
                    borderRadius: 8,
                    padding: 16,
                    background: "#fafafa",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <Typography.Text strong style={{ fontSize: 16 }}>
                      {p.name || `配件 ${i + 1}`}
                    </Typography.Text>
                    {p.oe_hint && (
                      <Tag color="blue" style={{ cursor: "pointer" }} icon={<CopyOutlined />} onClick={() => copy(p.oe_hint!)}>
                        OE：{p.oe_hint}
                      </Tag>
                    )}
                  </div>
                  {p.alternatives?.length ? (
                    <div style={{ marginTop: 10 }}>
                      <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                        可替换品牌件：
                      </Typography.Text>
                      <div style={{ marginTop: 6, display: "flex", flexWrap: "wrap", gap: 8 }}>
                        {p.alternatives.map((alt, j) => (
                          <Button key={j} size="small" onClick={() => copy(alt)}>
                            {alt}
                          </Button>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
            {parsed.notes ? (
              <Typography.Paragraph type="secondary" style={{ marginTop: 16, marginBottom: 0 }}>
                备注：{parsed.notes}
              </Typography.Paragraph>
            ) : null}
          </>
        ) : raw ? (
          <Typography.Paragraph>{raw}</Typography.Paragraph>
        ) : (
          <Empty description="输入配件需求后点击「AI 匹配」" />
        )}
      </ProCard>
    </PageContainer>
  );
}
