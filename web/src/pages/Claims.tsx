import { ModalForm, ProForm, ProFormText, ProFormTextArea, ProTable } from "@ant-design/pro-components";
import type { ProColumns } from "@ant-design/pro-components";
import { Button, message, Tag } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { getJSON, postJSON } from "../api/client";

interface Claim {
  id: number;
  case_no: string;
  status: string;
  stage: string | null;
  estimated_amount: number | null;
  service_order_no: string | null;
}

const statusColor: Record<string, string> = {
  reported: "blue",
  assessment: "orange",
  settled: "green",
};

export default function Claims() {
  const navigate = useNavigate();
  const columns: ProColumns<Claim>[] = [
    { title: "ID", dataIndex: "id", width: 70, search: false },
    {
      title: "案件号",
      dataIndex: "case_no",
      render: (_, r) => (
        <a onClick={() => navigate(`/claims/${r.id}`)}>{r.case_no}</a>
      ),
    },
    {
      title: "状态",
      dataIndex: "status",
      search: false,
      render: (_, r) => <Tag color={statusColor[r.status] || "default"}>{r.status}</Tag>,
    },
    { title: "阶段", dataIndex: "stage", search: false },
    { title: "预估金额", dataIndex: "estimated_amount", search: false, valueType: "money" },
    {
      title: "维修工单",
      dataIndex: "service_order_no",
      search: false,
      render: (v) => (v ? <Tag color="geekblue">{v as string}</Tag> : <Tag>未生成</Tag>),
    },
    { title: "操作", valueType: "option", render: (_, r) => [<a key="o" onClick={() => navigate(`/claims/${r.id}`)}>处理</a>] },
  ];

  return (
    <ProTable<Claim>
      rowKey="id"
      headerTitle="理赔管理"
      columns={columns}
      search={false}
      request={async () => {
        const data = await getJSON<Claim[]>("/claims").catch(() => []);
        return { data, success: true, total: data.length };
      }}
      toolBarRender={() => [
        <ModalForm
          key="add"
          title="新建理赔案"
          trigger={<Button type="primary" icon={<PlusOutlined />}>新建</Button>}
          modalProps={{ destroyOnClose: true }}
          onFinish={async (vals: Record<string, string>) => {
            const res = await postJSON<Claim>("/claims", vals);
            if (res?.service_order_no) {
              message.success(`已立案 ${res.case_no}，并自动创建维修工单 ${res.service_order_no}`);
            }
            return true;
          }}
        >
          <ProFormText name="vin" label="车架号 VIN" rules={[{ required: true }]} />
          <ProFormText name="insurance_company" label="保险公司" placeholder="人保/平安/太保…" />
          <ProFormText name="insurance_policy_no" label="保单号" />
          <ProFormText name="incident_at" label="出险时间" placeholder="2026-06-25 10:00" />
          <ProFormText name="incident_location" label="出险地点" />
          <ProFormTextArea name="description" label="事故描述" />
        </ModalForm>,
      ]}
    />
  );
}

export { ProForm };
