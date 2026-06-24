import { ProLayout } from "@ant-design/pro-components";
import type { MenuDataItem, ProSettings } from "@ant-design/pro-components";
import {
  DashboardOutlined,
  CarOutlined,
  FileProtectOutlined,
  FileTextOutlined,
  ToolOutlined,
  AppstoreOutlined,
  RobotOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { Dropdown } from "antd";
import { useAuth } from "../store/auth";

const menuRouteMap: Record<string, string> = {
  "/dashboard": "/",
  "/vehicles": "/vehicles",
  "/claims": "/claims",
  "/documents": "/documents",
  "/orders": "/orders",
  "/parts": "/parts",
  "/assistant": "/assistant",
};

const menu = [
  { path: "/dashboard", name: "工作台", icon: <DashboardOutlined /> },
  { path: "/claims", name: "理赔管理", icon: <FileProtectOutlined /> },
  { path: "/documents", name: "单证中心", icon: <FileTextOutlined /> },
  { path: "/vehicles", name: "车辆档案", icon: <CarOutlined /> },
  { path: "/orders", name: "维修工单", icon: <ToolOutlined /> },
  { path: "/parts", name: "配件匹配", icon: <AppstoreOutlined /> },
  { path: "/assistant", name: "智能助手", icon: <RobotOutlined /> },
];

const settings: Partial<ProSettings> = {
  layout: "mix",
  fixSiderbar: true,
  fixedHeader: true,
  navTheme: "light",
  colorPrimary: "#1677ff",
  contentWidth: "Fluid",
  title: "Carwork",
};

export default function BasicLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  return (
    <ProLayout
      {...settings}
      logo={false}
      location={{ pathname: location.pathname }}
      menuDataRender={() => menu as MenuDataItem[]}
      menuItemRender={(item, dom) => <Link to={item.path || "/"}>{dom}</Link>}
      onMenuHeaderClick={() => navigate("/")}
      avatarProps={{
        title: user?.name || "用户",
        size: "small",
        render: (_, dom) => (
          <Dropdown
            menu={{
              items: [
                {
                  key: "logout",
                  icon: <LogoutOutlined />,
                  label: "退出登录",
                  onClick: () => {
                    logout();
                    navigate("/login");
                  },
                },
              ],
            }}
          >
            {dom}
          </Dropdown>
        ),
      }}
    >
      <Outlet />
    </ProLayout>
  );
}

export { menuRouteMap };
