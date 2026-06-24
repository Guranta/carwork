import { ModalForm, ProFormText, ProFormDigit, ProTable } from "@ant-design/pro-components";
import type { ProColumns } from "@ant-design/pro-components";
import { Button, Popconfirm, Tag } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { getJSON, postJSON } from "../api/client";

interface Vehicle {
  id: number;
  vin: string;
  plate_no: string | null;
  brand: string | null;
  model: string | null;
  year: number | null;
  color: string | null;
}

export default function Vehicles() {
  const columns: ProColumns<Vehicle>[] = [
    { title: "ID", dataIndex: "id", width: 70, search: false },
    { title: "VIN", dataIndex: "vin", copyable: true, ellipsis: true },
    { title: "车牌号", dataIndex: "plate_no" },
    { title: "品牌", dataIndex: "brand", search: false },
    { title: "车型", dataIndex: "model", search: false },
    { title: "年份", dataIndex: "year", search: false },
    { title: "颜色", dataIndex: "color", search: false },
    {
      title: "操作",
      valueType: "option",
      render: () => [<a key="v">查看</a>, <Popconfirm key="d" title="演示版：仅展示"><a>删除</a></Popconfirm>],
    },
  ];

  return (
    <ProTable<Vehicle>
      rowKey="id"
      headerTitle="车辆档案"
      columns={columns}
      search={false}
      request={async () => {
        const data = await getJSON<Vehicle[]>("/vehicles").catch(() => []);
        return { data, success: true, total: data.length };
      }}
      toolBarRender={() => [
        <ModalForm<Vehicle>
          key="add"
          title="新增车辆"
          trigger={<Button type="primary" icon={<PlusOutlined />}>新增</Button>}
          modalProps={{ destroyOnClose: true }}
          onFinish={async (vals) => {
            await postJSON("/vehicles", vals);
            return true;
          }}
        >
          <ProFormText name="vin" label="VIN" placeholder="车架号" rules={[{ required: true }]} />
          <ProFormText name="plate_no" label="车牌号" placeholder="沪A12345" />
          <ProFormText name="brand" label="品牌" />
          <ProFormText name="model" label="车型" />
          <ProFormDigit name="year" label="年份" />
          <ProFormText name="color" label="颜色" />
        </ModalForm>,
      ]}
    />
  );
}

export { Tag };
