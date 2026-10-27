"""Minimal MCP (Model Context Protocol) server, mounted at /mcp.

Implements the handful of JSON-RPC 2.0 methods a plain "tools" server
needs: initialize, tools/list, tools/call. No resources, no sampling,
no server-initiated messages — so every request is answered directly,
which the Streamable HTTP transport (MCP spec 2025-03-26+) allows for
servers that never need to push a message on their own. This keeps the
whole thing inside the existing Flask/WSGI app, so it deploys with the
same `wrangler deploy` as the rest of the site, no extra Worker needed.
"""
import uuid

from flask import Blueprint, jsonify, request

from mcp_tools import TOOLS

mcp_bp = Blueprint("mcp", __name__)

PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "predictorian-weather", "version": "1.1.1"}


def _rpc_result(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _rpc_error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _tools_list_payload():
    return {
        "tools": [
            {
                "name": name,
                "description": spec["description"],
                "inputSchema": spec["inputSchema"],
            }
            for name, spec in TOOLS.items()
        ]
    }


def _call_tool(name, arguments):
    spec = TOOLS.get(name)
    if spec is None:
        raise KeyError(name)
    text = spec["fn"](**(arguments or {}))
    return {"content": [{"type": "text", "text": text}], "isError": False}


@mcp_bp.after_request
def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Mcp-Session-Id"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


@mcp_bp.route("/mcp", methods=["OPTIONS"])
def mcp_preflight():
    return "", 204


@mcp_bp.route("/mcp", methods=["GET"])
def mcp_info():
    # Some clients probe with GET before POSTing JSON-RPC; this server
    # never streams unsolicited messages, so plain info is enough here.
    return jsonify({"server": SERVER_INFO, "protocolVersion": PROTOCOL_VERSION})


@mcp_bp.route("/mcp", methods=["POST"])
def mcp_endpoint():
    try:
        body = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify(_rpc_error(None, -32700, "Parse error")), 400

    if not isinstance(body, dict):
        return jsonify(_rpc_error(None, -32600, "Invalid Request")), 400

    method = body.get("method")
    req_id = body.get("id")

    # Notifications carry no "id" and get no JSON-RPC response body.
    if method == "notifications/initialized":
        return "", 202

    if method == "initialize":
        payload = {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        }
        resp = jsonify(_rpc_result(req_id, payload))
        resp.headers["Mcp-Session-Id"] = uuid.uuid4().hex
        return resp

    if method == "tools/list":
        return jsonify(_rpc_result(req_id, _tools_list_payload()))

    if method == "tools/call":
        params = body.get("params") or {}
        name = params.get("name")
        arguments = params.get("arguments") or {}
        try:
            result = _call_tool(name, arguments)
        except KeyError:
            return jsonify(_rpc_error(req_id, -32601, f"Unknown tool: {name}")), 404
        except TypeError as exc:
            return jsonify(_rpc_error(req_id, -32602, f"Invalid params: {exc}")), 400
        except Exception as exc:  # tool crashed; report as a tool-level error
            return jsonify(
                _rpc_result(
                    req_id,
                    {
                        "content": [{"type": "text", "text": f"Tool error: {exc}"}],
                        "isError": True,
                    },
                )
            )
        return jsonify(_rpc_result(req_id, result))

    return jsonify(_rpc_error(req_id, -32601, f"Unknown method: {method}")), 404
