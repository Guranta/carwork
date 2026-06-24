import { useCallback, useState } from "react";
import { PageContainer, ProTable } from "@ant-design/pro-components";
import type { ProColumns } from "@ant-design/pro-components";
import { Button, message, Popconfirm, Tag, Upload } from "antd";
import { InboxOutlined, ThunderboltOutlined } from "@ant-design/icons";
import type { UploadProps } from "antd";
import { api, getJSON, postJSON } from "../api/client";

interface DocItem {
  id: number;
  type: string;
  object_key: string;
  status: string;
  confidence: number | null;
  extracted: Record<string, unknown> | null;
}

const { Dragger } = Upload;

export default function Documents() {
  const [reloadKey, setReloadKey] = useState(0);
  const [busyId, setBusyId] = useState<number | null>(null);

  const reload = useCallback(() => setReloadKey((k) => k + 1), []);

  const uploadProps: UploadProps = {
    name: "file",
    multiple: true,
    action: undefined,
    customRequest: async (options) => {
      const { file, onSuccess, onError } = options;
      const fd = new FormData();
      fd.append("file", file as File);
      fd.append("doc_type", "general");
      try {
        await api.post("/documents/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
        message.success(`${(file as File).name} 上传成功`);
        onSuccess?.({}, new XMLHttpRequest());
        reload();
      } catch (e) {
        onError?.(e as Error);
      }
    },
  };

  const columns: ProColumns<DocItem>[] = [
    { title: "ID", dataIndex: "id", width: 70 },
    { title: "类型", dataIndex: "type", render: (_, r) => <Tag>{r.type}</Tag> },
    { title: "对象键", dataIndex: "object_key", ellipsis: true, search: false },
    {
      title: "状态",
      dataIndex: "status",
      search: false,
      render: (_, r) => {
        const color: Record<string, string> = { uploaded: "default", extracted: "green", review: "orange", failed: "red" };
        return <Tag color={color[r.status] || "default"}>{r.status}</Tag>;
      },
    },
    { title: "置信度", dataIndex: "confidence", search: false, render: (v) => (v ? Number(v).toFixed(2) : "—") },
    {
      title: "抽取结果",
      dataIndex: "extracted",
      search: false,
      ellipsis: true,
      render: (v) => (v && Object.keys(v as object).length ? JSON.stringify(v) : "—"),
    },
    {
      title: "操作",
      valueType: "option",
      render: (_, r) => [
        <Popconfirm
          key="ex"
          title="调用 AI 进行 OCR 抽取？"
          onConfirm={async () => {
            setBusyId(r.id);
            try {
              const res = await postJSON<{ status: string; confidence: number; extracted: Record<string, unknown> }>(
                `/documents/${r.id}/extract`
              );
              message.success(`抽取完成（置信度 ${res.confidence ?? "—"}）`);
              reload();
            } finally {
              setBusyId(null);
            }
          }}
        >
          <a>
            <ThunderboltOutlined /> AI 抽取
          </a>
        </Popconfirm>,
      ],
    },
  ];

  return (
    <PageContainer header={{ title: "单证中心", breadcrumb: {} }}>
      <Dragger {...uploadProps} style={{ marginBottom: 16, padding: 8 }}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽上传单证（行驶证 / 驾驶证 / 保单 / 发票等）</p>
        <p className="ant-upload-hint">上传后可点击「AI 抽取」调用视觉 OCR + 结构化提取</p>
      </Dragger>

      <ProTable<DocItem>
        rowKey="id"
        search={false}
        key={reloadKey}
        columns={columns}
        loading={busyId !== null}
        request={async () => {
          // 后端暂无 documents 列表接口，按需扩展；这里读不到则空表
          const data = await getJSON<DocItem[]>("/documents").catch(() => []);
          return { data, success: true, total: data.length };
        }}
        toolBarRender={() => [<Button key="r" onClick={reload}>刷新</Button>]}
      />
    </PageContainer>
  );
}
