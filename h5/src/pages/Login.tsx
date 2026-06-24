import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, register } from "../api";
import { setToken } from "../api/client";

export default function Login() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("演示车主");
  const [account, setAccount] = useState("13800001234");
  const [password, setPassword] = useState("123456");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = mode === "login" ? await login(account, password) : await register(name, account, password);
      setToken(data.access_token);
      navigate("/", { replace: true });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : mode === "login" ? "登录失败" : "注册失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-hero">
        <span className="eyebrow">CARWORK AI</span>
        <h1>车险理赔助手</h1>
        <p>查保单、问进度、拍车损、估维修，一次对话搞定。</p>
      </section>

      <form className="auth-card" onSubmit={onSubmit}>
        <div className="segmented">
          <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>登录</button>
          <button type="button" className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>注册</button>
        </div>
        {mode === "register" && (
          <label>
            姓名
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="请输入姓名" />
          </label>
        )}
        <label>
          手机号
          <input value={account} onChange={(e) => setAccount(e.target.value)} placeholder="13800001234" />
        </label>
        <label>
          密码
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="123456" />
        </label>
        {error && <div className="form-error">{error}</div>}
        <button className="primary-btn" disabled={loading}>{loading ? "处理中..." : mode === "login" ? "进入助手" : "创建账号"}</button>
      </form>
    </main>
  );
}
