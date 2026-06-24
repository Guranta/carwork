import { LoginForm, ProFormText } from "@ant-design/pro-components";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { App, message } from "antd";
import { useNavigate, useLocation } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../store/auth";
import { postJSON } from "../api/client";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/";

  return (
    <div style={{ height: "100vh", background: "linear-gradient(135deg,#1677ff 0%,#0b3d91 100%)", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 380, background: "#fff", borderRadius: 12, padding: "32px 28px", boxShadow: "0 10px 40px rgba(0,0,0,.18)" }}>
        <LoginForm<{
          account: string;
          password: string;
        }>
          title="Carwork"
          subTitle="保险理赔 + 车后市场 AI 平台"
          submitter={{ searchConfig: { submitText: "登录" } }}
          onFinish={async (vals) => {
            setLoading(true);
            try {
              await login(vals.account, vals.password);
              message.success("登录成功");
              navigate(from, { replace: true });
            } catch {
              // 拦截器已提示
            } finally {
              setLoading(false);
            }
          }}
        >
          <ProFormText
            name="account"
            fieldProps={{ size: "large", prefix: <UserOutlined /> }}
            placeholder="手机号"
            rules={[{ required: true, message: "请输入手机号" }]}
          />
          <ProFormText.Password
            name="password"
            fieldProps={{ size: "large", prefix: <LockOutlined /> }}
            placeholder="密码"
            rules={[{ required: true, message: "请输入密码" }]}
          />
          <div style={{ marginBottom: 16, color: "#999", fontSize: 12 }}>
            首次使用？可
            <a
              onClick={async (e) => {
                e.preventDefault();
                try {
                  await postJSON("/auth/register", { name: "新用户", phone: "13800000001", password: "123456" });
                  message.success("已注册演示账号 13800000001 / 123456，请登录");
                } catch {
                  /* 已存在则忽略 */
                }
              }}
            >
              注册演示账号
            </a>
          </div>
        </LoginForm>
      </div>
    </div>
  );
}

export { App };
