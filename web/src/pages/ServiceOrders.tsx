import { ModalForm, ProFormText, ProFormTextArea, ProTable } from "@ant-design/pro-components";
import type { ProColumns } from "@ant-design/pro-components";
import { Button, Tag } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { getJSON, postJSON } from "../api/client";

interface Order {
  id: number;
  order_no: string;
  status: string;
  total_amount: number | null;
}

const statusColor: Record<string, string> = {
  created: "blue",
  in_progress: "orange",
  completed: "green",
};

export default function ServiceOrders() {
  const columns: ProColumns<Order>[] = [
    { title: "ID", dataIndex: "id", width: 70, search: false },
    { title: "工单号", dataIndex: "order_no" },
    { title: "故障/事故描述", dataIndex: "fault_desc", ellipsis: true, search: false },
    {
      title: "状态",
      dataIndex: "status",
      search: false,
      render: (_, r) => <Tag color={statusColor[r.status] || "default"}>{r.status}</Tag>,
    },
    { title: "金额", dataIndex: "total_amount", search: false, valueType: "money" },
  ];

  return (
    <ProTable<Order>
      rowKey="id"
      headerTitle="维修工单"
      search={false}
      columns={columns}
      request={async () => {
        const data = await getJSON<Order[]>("/aftermarket/orders").catch(() => []);
        return { data, success: true, total: data.length };
      }}
      toolBarRender={() => [
        <ModalForm
          key="add"
          title="新建工单"
          trigger={<Button type="primary" icon={<PlusOutlined />}>新建</Button>}
          modalProps={{ destroyOnClose: true }}
          onFinish={async (vals: Record<string, string>) => {
            await postJSON("/aftermarket/orders", vals);
            return true;
          }}
        >
          <ProFormText name="vin" label="车架号 VIN" />
          <ProFormTextArea name="fault_desc" label="故障描述" />
        </ModalForm>,
      ]}
    />
  );
}
