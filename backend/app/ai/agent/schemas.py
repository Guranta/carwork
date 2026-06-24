"""Agent 工具的 OpenAI function-calling schema(描述+参数)，喂给 DeepSeek 的 tools 参数。

MVP 不启用 strict 模式以保持参数灵活；required 只列必填项。
"""

AGENT_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "query_policy",
            "description": (
                "查询保单条款(险种/免赔额/赔付比例/保额/是否承保车辆损失)。"
                "用于判断能否理赔本车损伤、计算报销价。至少提供 policy_no / plate_no / vin 之一。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "policy_no": {"type": "string", "description": "保单号"},
                    "plate_no": {"type": "string", "description": "车牌号，如 京A12345"},
                    "vin": {"type": "string", "description": "车架号(VIN)，17 位"},
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_claim_status",
            "description": "按案件编号查询理赔案件的当前阶段(报案/定损/理算/核赔/赔付)与进度、估损/赔付金额。",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_no": {"type": "string", "description": "理赔案件编号，如 CL20260625XXXXXX"}
                },
                "required": ["case_no"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_repair_shop",
            "description": "按用户当前经纬度查找最近的合作修理厂(直线距离排序)，返回名称/地址/电话/距离/工时单价/评分。",
            "parameters": {
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "用户纬度"},
                    "lng": {"type": "number", "description": "用户经度"},
                    "top_n": {"type": "integer", "description": "返回数量，默认 3", "default": 3},
                    "city": {"type": "string", "description": "可选，限定城市，如 上海"},
                },
                "required": ["lat", "lng"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_cost",
            "description": (
                "按损伤清单估算【自费维修价】(工时费+配件费，不含保险理赔)。"
                "通常先用 assess_damage 识别损伤，再把其 damages 传入本工具算价。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "damages": {
                        "type": "array",
                        "description": "损伤清单",
                        "items": {
                            "type": "object",
                            "properties": {
                                "part": {"type": "string", "description": "部位，如 前保险杠"},
                                "repair": {
                                    "type": "string",
                                    "description": "维修方式: 喷漆/钣金/更换",
                                },
                            },
                        },
                    }
                },
                "required": ["damages"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assess_damage",
            "description": (
                "识别用户刚上传的车辆损伤照片，输出损伤清单(部位/类型/程度/建议维修方式)与置信度。"
                "无需传图片参数(系统自动使用用户最近上传的图片)。可在 focus 指定重点部位。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "focus": {"type": "string", "description": "可选，重点关注部位，如 前保险杠"},
                },
                "additionalProperties": False,
            },
        },
    },
]
